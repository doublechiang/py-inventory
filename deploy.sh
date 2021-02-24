#!/bin/bash
yum install python3
wget http://10.16.0.1/py-inventory/inventory.py
wget http://10.16.0.1/py-inventory/requirements.txt
pip3 install -r requirements.txt
python3 inverntory.py
