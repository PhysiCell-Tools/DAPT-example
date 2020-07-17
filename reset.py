"""
Reset the repository by removing simulation data.

This script will:
* Remove the contens of the ./outputs folder and adds an empty file to it
* Removes the outputs created by PhysiCell (using `make data-cleanup`)
* If the `--hard` flag is included (`python reset.py --hard`), it will remove PhysiCell compiled files
"""

import os, sys, csv, shutil
from pathlib import Path

db_path = 'parameters.csv'

# Not used as parameters.csv isn't edited
'''
print('Reseting Parameters')

with open(db_path, 'w') as f:
    writer = csv.DictWriter(f, fieldnames=['id', 'status', 'start-time', 'end-time', 'comment', './overall/max_time','./user_parameters/number_of_workers'])
    writer.writeheader()
    writer.writerow({'id':'test1', 'status':'', 'start-time':'', 'end-time':'', 'comment':'', './overall/max_time':'2880', './user_parameters/number_of_workers':'5', })
    writer.writerow({'id':'test2', 'status':'', 'start-time':'', 'end-time':'', 'comment':'', './overall/max_time':'2880', './user_parameters/number_of_workers':'50', })
    writer.writerow({'id':'test3', 'status':'', 'start-time':'', 'end-time':'', 'comment':'', './overall/max_time':'2880', './user_parameters/number_of_workers':'150', })
'''

# Remove images we moved
shutil.rmtree('outputs/')
os.mkdir('outputs/')
Path('outputs/empty.txt').touch()

# Remove CSVs created by simulations
if os.path.exists('basic_params.csv'):
    os.remove('basic_params.csv')
if os.path.exists('config_params.csv'):
    os.remove('config_params.csv')

# Remove config files
if os.path.exists('config_config.json'):
    os.remove('config_config.json')

# Cleanup PhysiCell
os.system('make -C PhysiCell data-cleanup')

if '--hard' in sys.argv:
    os.system('make -C PhysiCell clean')
