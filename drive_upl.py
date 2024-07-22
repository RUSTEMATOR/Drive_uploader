import os
import time
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import gspread
from oauth2client.service_account import ServiceAccountCredentials


start_time = time.time()

gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)



scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = gauth.credentials
client = gspread.authorize(creds)

folder_path = "./Deposit_bible_screenshots"


def get_or_create_folder(folder_name):
    file_list = drive.ListFile({'q': f"title='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"}).GetList()
    
    if file_list:
        # Folder exists
        return file_list[0]['id']
    else:
        # Folder does not exist, create it
        folder_metadata = {
            'title': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = drive.CreateFile(folder_metadata)
        folder.Upload()
        return folder['id']
    

folder_id = get_or_create_folder('Kb_dep_bible_screenshots')



# Create a new spreadsheet using gspread
spreadsheet = client.create('Uploaded PNG Files Links')
spreadsheet_id = spreadsheet.id

 
file = drive.CreateFile({'id': spreadsheet_id})
file.Upload()
file['parents'] = [{'id': folder_id}]
file.Upload()


worksheet = spreadsheet.get_worksheet(0)




def find_png_files(directory):
    png_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.png'):
                png_files.append(os.path.join(root, file))
    return png_files

png_files = find_png_files(folder_path)




links = []

for file_path in png_files:
    filename = os.path.basename(file_path)
    file = drive.CreateFile({'title': filename, 'parents': [{'id': folder_id}]})
    file.SetContentFile(file_path)
    file.Upload()
    file_link = file['alternateLink']
    links.append((filename, file_link))


worksheet.append_row(['Filename', 'Link'])
for filename, link in links:
    worksheet.append_row([filename, link])

end_time = time.time()
elapsed_time = end_time - start_time

print("All .png files have been uploaded and links are stored in the Google Spreadsheet.")
print(f"Process completed in {elapsed_time:.2f} seconds.")


