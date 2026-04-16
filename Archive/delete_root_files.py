#!/usr/bin/env python3
"""
Google Drive - Gyökér mappa fájljainak törlése
Töröli az UST_Uzsoki_Márk és Szülői egyéni beszélgetések - 8.a fájlokat
"""

import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive']

# Törlendő fájl ID-k
FILES_TO_DELETE = {
    '1qiS774F79bA-AZgHuOKKRQFlRI4NgAn09FYIxQEjREE': 'UST_Uzsoki_Márk',
    '1xsq9798JSQC9Du-yQSH2PXepEOQ36uUR8_003q9m_2E': 'Szülői egyéni beszélgetések - 8.a'
}


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


def main():
    print("=" * 80)
    print("FÁJLOK TÖRLÉSE")
    print("=" * 80)
    print()

    service = authenticate()
    print("OK - Bejelentkezés sikeres\n")

    deleted_count = 0

    for file_id, file_name in FILES_TO_DELETE.items():
        try:
            service.files().delete(fileId=file_id).execute()
            print(f"OK - TOROLT: {file_name}")
            deleted_count += 1
        except Exception as e:
            print(f"HIBA: {file_name} - {str(e)}")

    print("\n" + "=" * 80)
    print(f"Torolt fajlok: {deleted_count}/{len(FILES_TO_DELETE)}")
    print("=" * 80)


if __name__ == '__main__':
    main()
