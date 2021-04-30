"""
Basic DAPT Example
==================

This script demonstrates the simplest example of parameter testing in PhysiCell using DAPT.
"""

import os, platform
import xml.etree.ElementTree as ET
import dapt


 # This is the same method implimented in `dapt.tools.create_XML()`.  
 # The method was coppied here to make the code easier to read.
def create_XML(parameters, default_settings="PhysiCell_settings_default.xml", save_settings="PhysiCell_settings.xml", off_limits=[]):
    """
    Create a PhysiCell XML settings file given a dictionary of paramaters.  This function works by having a ``default_settings`` file which contains the generic XML structure.  Each key in ``parameters` then contains the paths to each XML tag in the ``default_settings`` file.  The value of that tag is then set to the value in the associated key.  If a key in ``parameters`` does not exist in the ``default_settings`` XML file then it is ignored.  If a key in ``parameters`` also exists in ``off_limits`` then it is ignored.

    Args:
        paramaters (dict): A dictionary of paramaters where the key is the path to the xml variable and the value is the desired value in the XML file.
        default_settings (str): the path to the default xml file
        save_settings (str): the path to the output xml file
        off_limits (list): a list of keys that should not be inserted into the XML file.
    """

    parameters = dict(parameters)
    tree = ET.parse(default_settings)
    root = tree.getroot()

    for key in parameters:
        if key in off_limits:
            next

        node = root.find(key)

        if node != None:
            node.text = str(parameters[key])

    tree.write(save_settings)


# Set up DAPT objects: database (Delimited_file) and parameter manager (Param)
db = dapt.db.Delimited_file('parameters.csv', delimiter=',')
params = dapt.Param(db)

# Get the first parameter.  Returns None if there are none
p = params.next_parameters()

while p is not None:

    print("Request parameters: %s" % p)

    params.update_status(p["id"], 'updating PhysiCell settings')

    # Update the default settings with the given parameters
    create_XML(p, default_settings="PhysiCell_settings_default.xml", save_settings="PhysiCell_settings.xml")

    params.update_status(p["id"], 'running simulation')

    # Run PhysiCell (execution method depends on OS)
    if platform.system() == 'Windows':
        os.system("biorobots.exe")
    else:
        os.system("./biorobots")

    # Update sheets to mark the test is finished
    params.successful(p["id"])

    #Get the next parameter
    p = params.next_parameters()
