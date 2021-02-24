#!/usr/bin/env python3
# python factory module
import subprocess
import json
import os
import logging
import requests
import datetime

# third party module
import xml.etree.ElementTree as ET

# local module

class Inventory:

    def getBmcMac(self):
        cmd = 'ipmitool lan print'
        mac = None
        try:
            result = subprocess.run(cmd.split(), universal_newlines=True, stdout=subprocess.PIPE)
        except FileNotFoundError:
            print('ipmitool not installed.')
        for line in result.stdout.splitlines():
            if 'MAC Address' in line:
                sep = line.find(':')
                mac = line[sep+1:].strip()
        return mac

    def getNics(self):
        """ use lshw -class network -xml
        """
        try:
            cmd = "lshw -class network -xml"
            result=subprocess.run(cmd.split(), universal_newlines = True, stdout=subprocess.PIPE).stdout
            # result = open('seeds/lshw_net.xml').read()
        except FileNotFoundError:
            logging.error("Can't find the lshw executable")

        root = ET.fromstring(result)
        devs = root.findall('node')
        nic = dict()
        nics = []
        for node in devs:
            attribs = 'product vendor physid serial businfo'.split()
            # USB are ignored.
            # multiple port (physid with .) are ignored.
            if node.find('businfo') is not None and 'usb' in node.find('businfo').text:
                    continue
            if node.find('physid') is not None and '.' in node.find('physid').text:
                    continue
            nic= self.__map_xml_dict(node, attribs)
            nics.append(nic)
        return nics


    def getStorage(self):
        try:
            cmd = "lshw -class storage -xml"
            result=subprocess.run(cmd.split(), universal_newlines = True, stdout=subprocess.PIPE).stdout
            # result = open('seeds/lshw_raid.xml').read()
        except FileNotFoundError:
            logging.error("Can't find the lshw executable")

        root = ET.fromstring(result)
        devs = root.findall('node')
        stor = dict()
        stors = []
        for node in devs:
            attribs = 'description product vendor businfo'.split()
            # USB bus are ignored.
            # Build-in SATA controller with PCI bus 0 are ignored.
            if node.find('businfo') is not None:
                businfo = node.find('businfo').text
                if 'usb' in businfo:
                    continue
                if 'pci' in businfo:
                    pcibusno = businfo.split(':')[1]
                    if pcibusno == '00':
                        continue
                
            stor= self.__map_xml_dict(node, attribs)
            stors.append(stor)
        return stors

    def getDisks(self):
        try:
            cmd = "lshw -class disk -xml"
            result=subprocess.run(cmd.split(), universal_newlines = True, stdout=subprocess.PIPE).stdout
            # result= open('seeds/lshw_disk.xml').read()
        except FileNotFoundError:
            logging.error("Can't find the lshw executable")

        root = ET.fromstring(result)
        devs = root.findall('node')
        disk = dict()
        disks = []
        for node in devs:
            attribs = 'description product version serial businfo'.split()
            # skip CDROM
            if 'cdrom' in node.attrib['id']:
                continue
                
            disk= self.__map_xml_dict(node, attribs)
            disks.append(disk)
        return disks


    def getMemory(self):
        try:
            cmd = "lshw -class memory -xml"
            result=subprocess.run(cmd.split(), universal_newlines = True, stdout=subprocess.PIPE).stdout
            # result = open('seeds/lshw_mem.xml').read()
        except FileNotFoundError:
            logging.error("Can't find the lshw executable")

        root = ET.fromstring(result)
        devs = root.findall('node/node')
        mem = dict()
        mems = []
        for node in devs:
            # print(node.tag, node.attrib)
            size = node.find('size')
            if size is not None:
                attribs = 'description product vendor physid serial slot size'.split()
                mem = self.__map_xml_dict(node, attribs)
                mems.append(mem)
        return mems

    def getCpus(self):
        try:
            cmd = "lshw -class processor -xml"
            result=subprocess.run(cmd.split(), universal_newlines = True, stdout=subprocess.PIPE).stdout
            # result = open('seeds/lshw_proc.xml').read()
        except FileNotFoundError:
            logging.error("Can't find the lshw executable")

        root = ET.fromstring(result)
        cpudevs = root.findall('node')
        cpu = dict()
        cpus = []
        for module in cpudevs:
            attribs = 'product slot'.split()
            cpu = self.__map_xml_dict(module, attribs)
            cpus.append(cpu)
        return cpus

    def getNvmes(self):
        """ lshw don't report serial number and do not have the model name
        """
        block_root = '/sys/block/'
        path = os.walk(block_root)
        nvmes = []
        for root, dirs, files in path:
            for dir in dirs:
                if 'nvme' in dir:
                    nvme = dict()
                    attribs = 'model serial firmware_rev address'.split()
                    for attr in attribs:
                        nvme[attr] = open(dir + '/device/' + attr).read()
                    nvmes.append(nvme)
        return nvmes


    def __map_xml_dict(self, element, attrs:list):
        """ store the xml elementry tree attributes into dictionary
        """
        value = dict()
        for attr in attrs:
            if element.find(attr) is not None:
                value[attr] = element.find(attr).text
                if attr == 'size':
                    # size in bytes, convert to GB
                    value[attr] = str(int(int(value[attr])/1024/1024/1024)) + 'G'

        return value

    def getSysInventory(self):
        self.sys['bmc'] = self.getBmcMac()
        self.sys['timestamp'] = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        self.sys['nvmes'] = self.getNvmes()
        self.sys['nics'] = self.getNics()
        self.sys['storage'] = self.getStorage()
        self.sys['cpus'] = self.getCpus()
        self.sys['mems'] = self.getMemory()
        self.sys['disks'] = self.getDisks()
        return self
           
    def sendInventory(self, url, data):
        """ data: varialbe holding json structure to host
        """
        requests.post(url, data=json.dumps(data))

    def __str__(self):
        return json.dumps(self.sys)
    
    def __init__(self):
        self.sys = dict()


 

# print(Inventory().getSysInventory())
inv = json.loads(open('inv.json').read())
Inventory().sendInventory('http://localhost:4567/inventories/create', inv)








