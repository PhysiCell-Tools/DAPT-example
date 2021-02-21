import os, platform
import dapt

config = dapt.Config(path='config.json')
db = dapt.db.Delimited_file('parameters.csv', delimiter=',')
ap = dapt.Param(db, config=config)

parameters = ap.next_parameters()

while parameters is not None:
    dapt.tools.create_XML(parameters, default_settings="PhysiCell_settings_default.xml", save_settings="PhysiCell_settings.xml")

    if platform.system() == 'Windows':
        os.system("biorobots.exe")
    else:
        os.system("./biorobots")

    ap.successful(parameters["id"])
    parameters = ap.next_parameters()
