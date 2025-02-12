import os
import pickle
import io
import shutil
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# If modifying the scope, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
IMAGE_FOLDER = "images"

def authenticate_google_account():
    """Authenticate and return a Google Drive API service."""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('drive', 'v3', credentials=creds)

def get_drive_images(service, folder_id):
    """Get a list of image file names from Google Drive."""
    query = f"'{folder_id}' in parents and mimeType contains 'image/'"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    return {file['name']: file['id'] for file in results.get('files', [])}

def sync_and_download_images(service, folder_id, download_dir=IMAGE_FOLDER):
    """Delete images not in Drive, then download new ones."""
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    # Get current images from Google Drive
    drive_images = get_drive_images(service, folder_id)
    
    # Get local images
    local_images = set(os.listdir(download_dir))

    # Delete local images that are no longer in Google Drive
    for image in local_images:
        if image not in drive_images:
            os.remove(os.path.join(download_dir, image))
            print(f"Deleted local file: {image}")

    # Download new images
    for image_name, file_id in drive_images.items():
        if image_name not in local_images:  # Only download if not already present
            print(f"Downloading {image_name}...")
            request = service.files().get_media(fileId=file_id)
            with open(os.path.join(download_dir, image_name), 'wb') as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    print(f"Download {int(status.progress() * 100)}%.")

if __name__ == '__main__':
    folder_id = '1bGH2eoTDULTBNtIukgmCkYhDYq8xC6kM'  # Your Drive folder ID
    service = authenticate_google_account()
    sync_and_download_images(service, folder_id)
