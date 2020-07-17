"""
PhysiCell Example
=================

This file shows an example workflow with PhysiCell.
"""

import os,platform,datetime, time
import dapt

conf = dapt.Config('config.json')
sheet = dapt.Delimited_file('parameters.csv', delimiter=',')
ap = dapt.Param(sheet, conf)
box = dapt.Box(config = conf)
box.connect()

print("Starting main script")

parameters = ap.next_parameters() #Get the next parameter

while parameters is not None:

    if parameters == None:
        print("No more parameters to run!")
        break

    print("Request parameters: %s" % parameters)

    try:
        # Reset from the previous run
        print("Cleaning up folder")
        dapt.tools.data_cleanup(conf)
        ap.update_status(parameters['id'], 'clean')

        # Create the parameters
        print("Creating parameters xml and autoParamSettings.txt")
        dapt.tools.create_XML(parameters, default_settings="config/PhysiCell_settings_default.xml", save_settings="config/PhysiCell_settings.xml")
        dapt.tools.create_settings_file(parameters)
        ap.update_status(parameters['id'], 'xml')

        # Run PhysiCell
        print("Running test")
        if platform.system() == 'Windows':
            os.system("AMIGOS-invasion.exe")
        else:
            os.system("./AMIGOS-invasion")
        ap.update_status(parameters['id'], 'sim')

        # Upload zip to box
        print("Uploading zip to box")
        if platform.system() == 'Windows':
            print(box.uploadFile(conf.config['boxFolderID'], '\\', fileName))
            print(box.uploadFile(conf.config['boxFolderZipID'], '\\', zipName))
        else:
            print(box.uploadFile(conf.config['boxFolderID'], '/'+fileName, fileName))
            print(box.uploadFile(conf.config['boxFolderZipID'], '/'+fileName, zipName))

            ap.update_status(parameters['id'], 'upload')

        # Update sheets to mark the test is finished
        ap.successful(parameters["id"]) #Test completed successfully so we need to mark it as such
        
    except ValueError:
        print("Test failed:")
        print(ValueError)
        ap.failed(parameters["id"], ValueError)
        
    