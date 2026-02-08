from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

def upload_excel(path):
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)

    file = drive.CreateFile({'title': 'HEDGEFUND_TERMINAL.xlsx'})
    file.SetContentFile(path)
    file.Upload()
