"""
Config DAPT and PhysiCell Example
================================

This script demonstrates the simplest example of parameter testing in PhysiCell using DAPT.
"""

import os, platform, csv, shutil, dapt

def main(db_path, config_path):

    # Set up DAPT objects: database (Delimited_file) and parameter manager (Param)
    config = dapt.Config(path=config_path)
    db = dapt.db.Delimited_file(db_path, delimiter=',')
    ap = dapt.Param(db, config=config)

    print("Starting main script")

    # Get the first parameter.  Returns None if there are none
    parameters = ap.next_parameters()

    while parameters is not None:

        print("Request parameters: %s" % parameters)

        # Use a try/except to report errors if they occur during the pipeline
        try:
            # Reset PhysiCell from the previous run using PhysiCell's data-cleanup
            print("Cleaning up folder")
            ap.update_status(parameters['id'], 'clean')
            os.system("make data-cleanup")

            # Update the default settings with the given parameters
            print("Creating parameters xml")
            ap.update_status(parameters['id'], 'xml')
            dapt.tools.create_XML(parameters, default_settings="config/PhysiCell_settings_default.xml", save_settings="config/PhysiCell_settings.xml")

            # Run PhysiCell (execution method depends on OS)
            print("Running test")
            ap.update_status(parameters['id'], 'sim')
            if platform.system() == 'Windows':
                os.system("biorobots.exe")
            else:
                os.system("./biorobots")

            # Moving final image to output folder
            ap.update_status(parameters['id'], 'output')
            shutil.copyfile('output/final.svg', '../outputs/%s_final.svg' % parameters["id"])

            # Update sheets to mark the test is finished
            ap.successful(parameters["id"])

        except ValueError:
            print("Test failed:")
            print(ValueError)
            ap.failed(parameters["id"], ValueError)

        parameters = ap.next_parameters() #Get the next parameter

if __name__ == '__main__':
    os.chdir('PhysiCell')

    master_db_path = '../parameters.csv'
    db_path = '../config_params.csv'
    master_config_path = '../config.json'
    config_path = '../config_config.json'

    shutil.copyfile(master_db_path, db_path)
    shutil.copyfile(master_config_path, config_path)

    main(db_path, config_path)
