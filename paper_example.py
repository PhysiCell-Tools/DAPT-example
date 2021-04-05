import os, platform
import dapt

config = dapt.Config(path='config.json')
db = dapt.db.Delimited_file('parameters.csv', delimiter=',')
params = dapt.Param(db, config=config)

p = params.next_parameters()

while p is not None:
    p['./save/folder'] = 'output/%s' % p['id']
    dapt.tools.create_XML(p, default_settings="PhysiCell_settings_default.xml", save_settings="PhysiCell_settings.xml")

    params.update_status(p["id"], 'running simulation')

    if platform.system() == 'Windows':
        os.system("biorobots.exe")
    else:
        os.system("./biorobots")

    params.successful(p["id"])
    p = params.next_parameters()
