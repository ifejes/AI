#!/usr/bin/env python3
"""
Google Drive - AI mappa és almappák létrehozása
"""

import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive']


def authenticate():
    """Bejelentkezés OAuth2.0-val"""
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('drive', 'v3', credentials=creds)


def create_folder(service, folder_name, parent_id=None):
    """Mappa létrehozása"""
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }

    if parent_id:
        file_metadata['parents'] = [parent_id]

    folder = service.files().create(
        body=file_metadata,
        fields='id, name'
    ).execute()

    return folder


def main():
    print("=" * 80)
    print("AI MAPPA LÉTREHOZÁSA")
    print("=" * 80)
    print()

    service = authenticate()
    print("OK - Bejelentkezés sikeres\n")

    # 1. AI mappa létrehozása
    print("..AI mappa létrehozása...")
    ai_folder = create_folder(service, 'AI')
    ai_folder_id = ai_folder['id']
    print(f"OK - Létrehozva: {ai_folder['name']} (ID: {ai_folder_id})\n")

    # 2. Almappák létrehozása
    subfolders = ['Gemini', 'ChatGPT', 'Claude']

    for subfolder_name in subfolders:
        print(f"..{subfolder_name} mappa létrehozása...")
        subfolder = create_folder(service, subfolder_name, ai_folder_id)
        print(f"OK - Létrehozva: {subfolder['name']} (ID: {subfolder['id']})")

    print("\n" + "=" * 80)
    print("MAPPÁK SIKERESEN LÉTREHOZVA!")
    print("=" * 80)
    print("\nMappastruktúra:")
    print("  AI/")
    for subfolder in subfolders:
        print(f"    ├─ {subfolder}/")
    print("=" * 80)


if __name__ == '__main__':
    main()
