#!/usr/bin/env python3
# python factory module
import subprocess
import json

# third party module
import xml.etree.ElementTree as ET

# local module

class Inventroy:

    def getNics(self):
        """ use lshw -class network -xml
        """
        try:
            # cmd = "lshw -class memory -xml"
            # result=subprocess.run(cmd.split(), universal_newlines = True, stdout=subprocess.PIPE)
            with open('seeds/lshw_net.xml') as f:
                result = f.read()
        except FileNotFoundError:
            print("Can't find the lshw executable")

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
            # cmd = "lshw -class storage -xml"
            # result=subprocess.run(cmd.split(), universal_newlines = True, stdout=subprocess.PIPE)
            with open('seeds/lshw_raid.xml') as f:
                result = f.read()
        except FileNotFoundError:
            print("Can't find the lshw executable")

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
            # cmd = "lshw -class disk -xml"
            # result=subprocess.run(cmd.split(), universal_newlines = True, stdout=subprocess.PIPE)
            with open('seeds/lshw_disk.xml') as f:
                result = f.read()
        except FileNotFoundError:
            print("Can't find the lshw executable")

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
            # cmd = "lshw -class memory -xml"
            # result=subprocess.run(cmd.split(), universal_newlines = True, stdout=subprocess.PIPE)
            with open('seeds/lshw_mem.xml') as f:
                result = f.read()
        except FileNotFoundError:
            print("Can't find the lshw executable")

        root = ET.fromstring(result)
        devs = root.findall('node/node')
        mem = dict()
        mems = []
        for node in devs:
            # print(module.tag, module.attrib)
            size = node.find('size')
            if size is not None:
                attribs = 'description product vendor physid serial slot size'.split()
                mem = self.__map_xml_dict(module, attribs)
                mems.append(mem)
        return mems

    def getCpu(self):
        try:
            # cmd = "lshw -class processor -xml"
            # result=subprocess.run(cmd.split(), universal_newlines = True, stdout=subprocess.PIPE)
            with open('seeds/lshw_proc.xml') as f:
                result = f.read()
        except FileNotFoundError:
            print("Can't find the lshw executable")

        root = ET.fromstring(result)
        cpudevs = root.findall('node')
        cpu = dict()
        cpus = []
        for module in cpudevs:
            attribs = 'product slot'.split()
            cpu = self.__map_xml_dict(module, attribs)
            cpus.append(cpu)
        return cpus

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
           
 

#print(Inventroy().getMemory()) 
#print(Inventroy().getCpu())
#print(Inventroy().getNic())
#print(Inventroy().getStorage())
print(Inventroy().getDisks())







