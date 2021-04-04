import os, platform
import dapt, gspread

# Update these variables
spreedsheet_id = ''
credentials_path = ''


config = dapt.Config(path='config.json')
db = dapt.db.Sheets(spreedsheet_id=spreedsheet_id, creds_path=credentials_path)
db.connect()
params = dapt.Param(db, config=config)

def reset_spreadsheet():
    data = []
    with open('parameters.csv', 'r') as csv:
        for c in csv:
            data.append(c.split(','))

    start = gspread.utils.rowcol_to_a1(1, 1)
    end = gspread.utils.rowcol_to_a1(len(data)+1, len(data[0])+1)

    range_label = '%s!%s:%s' % (db.worksheet().title, start, end)

    db.sheet.values_update(range_label, params={'valueInputOption': 'RAW'}, body={'values': data})


def main():

    p = params.next_parameters()

    while p is not None:
        dapt.tools.create_XML(p, default_settings="PhysiCell_settings_default.xml", save_settings="PhysiCell_settings.xml")

        params.update_status(p["id"], 'running simulation')

        if platform.system() == 'Windows':
            os.system("biorobots.exe")
        else:
            os.system("./biorobots")

        params.successful(p["id"])
        p = params.next_parameters()

if __name__ == '__main__':
    reset_spreadsheet()
    main()
