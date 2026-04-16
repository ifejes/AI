#!/usr/bin/env python3
"""
Gyökér fájlok listázása - részletes analízis
"""

import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive']


def authenticate():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)


def main():
    print("=" * 80)
    print("GYÖKÉR FÁJLOK ANALÍZISE")
    print("=" * 80)

    service = authenticate()
    print("OK - Bejelentkezés sikeres\n")

    query = "trashed = false"
    results = service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name, mimeType, parents)',
        pageSize=1000
    ).execute()

    all_files = results.get('files', [])

    print(f"Összesen fájl: {len(all_files)}\n")
    print("Gyökér fájlok (nincs parent):")
    print("-" * 80)

    root_files = []
    for file in all_files:
        if 'parents' not in file or not file['parents']:
            if file['mimeType'] != 'application/vnd.google-apps.folder':
                root_files.append(file)
                print(f"  • {file['name']}")
                print(f"    ID: {file['id']}")
                print(f"    Type: {file['mimeType']}")
                print(f"    Parents: {file.get('parents', [])}")
                print()

    print(f"\nÖsszesen gyökér fájl: {len(root_files)}")


if __name__ == '__main__':
    main()
