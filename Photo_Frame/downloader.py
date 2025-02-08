import os
import pickle
import io
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# If modifying the scope, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def authenticate_google_account():
    """Authenticate and return a Google Drive API service."""
    creds = None
    # The file token.pickle stores the user's access and refresh tokens.
    # It is created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    service = build('drive', 'v3', credentials=creds)
    return service

def download_images_from_drive(service, folder_id, download_dir="images"):
    """Download images from a specific Google Drive folder."""
    # Create the download directory if it doesn't exist
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    
    # Query the Google Drive folder for image files
    query = f"'{folder_id}' in parents and mimeType contains 'image/'"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])
    
    if not files:
        print('No images found.')
    else:
        for file in files:
            print(f"Downloading {file['name']}...")
            request = service.files().get_media(fileId=file['id'])
            fh = io.FileIO(os.path.join(download_dir, file['name']), 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print(f"Download {int(status.progress() * 100)}%.")
    print("All images downloaded.")

if __name__ == '__main__':
    folder_id = '1bGH2eoTDULTBNtIukgmCkYhDYq8xC6kM'  # Replace with your Google Drive folder ID
    service = authenticate_google_account()
    download_images_from_drive(service, folder_id)
