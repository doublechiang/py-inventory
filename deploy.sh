#!/bin/bash
yum install python3
wget --backups=1 http://10.16.0.1/py-inventory/inventory.py
wget --backups=1 http://10.16.0.1/py-inventory/requirements.txt
pip3 install -r requirements.txt
python3 inventory.py --target http://10.16.0.1/inventories/create
