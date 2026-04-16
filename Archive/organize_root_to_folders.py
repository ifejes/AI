#!/usr/bin/env python3
"""
Google Drive - Gyökér fájlok szervezése mappákba
Csak a gyökér mappában lévő fájlokat szervezem
"""

import os
from collections import defaultdict

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive']


class RootFileOrganizer:
    def __init__(self):
        self.service = None
        self.files_cache = {}
        self.folders = {}
        self.created_folders = {}

    def authenticate(self):
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

        self.service = build('drive', 'v3', credentials=creds)
        print("OK - Bejelentkezés sikeres")

    def get_all_files(self):
        """Lekéri az összes fájlt és mappát"""
        print("\n..Fájlok lekérése...")

        query = "trashed = false"
        results = self.service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name, mimeType, parents)',
            pageSize=1000
        ).execute()

        files = results.get('files', [])

        for file in files:
            self.files_cache[file['id']] = file
            if file['mimeType'] == 'application/vnd.google-apps.folder':
                self.folders[file['id']] = file['name']

        print(f"OK - Összesen {len(files)} fájl/mappa")

    def get_root_files(self):
        """Lekéri csak a gyökér mappában lévő fájlokat"""
        root_files = []
        for file_id, file_info in self.files_cache.items():
            if 'parents' not in file_info or not file_info['parents']:
                if file_info['mimeType'] != 'application/vnd.google-apps.folder':
                    root_files.append(file_info)
        return root_files

    def categorize_file(self, file_name: str, mime_type: str) -> str:
        """Fájl kategorizálása"""
        name_lower = file_name.lower()
        mime_lower = mime_type.lower()

        # Kategória meghatározása
        if 'image' in mime_lower or any(ext in name_lower for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
            return 'Images'
        elif 'video' in mime_lower or any(ext in name_lower for ext in ['.mp4', '.avi', '.mov', '.mkv']):
            return 'Videos'
        elif 'audio' in mime_lower or any(ext in name_lower for ext in ['.mp3', '.wav', '.m4a']):
            return 'Audio'
        elif 'pdf' in mime_lower or name_lower.endswith('.pdf'):
            return 'PDFs'
        elif 'document' in mime_lower or 'spreadsheet' in mime_lower or 'presentation' in mime_lower:
            return 'Documents'
        elif any(ext in name_lower for ext in ['.xlsx', '.xls', '.csv']):
            return 'Documents'
        elif any(ext in name_lower for ext in ['.pptx', '.ppt', '.odp']):
            return 'Documents'
        elif any(ext in name_lower for ext in ['.zip', '.rar', '.7z', '.tar']):
            return 'Archives'
        elif any(ext in name_lower for ext in ['.html', '.htm']):
            return 'Documents'
        elif any(ext in name_lower for ext in ['.vsdx', '.visio', '.vsd']):
            return 'Diagrams'
        else:
            return 'Egyéb'

    def find_or_create_folder(self, folder_name: str) -> str:
        """Mappa keresése vagy létrehozása"""
        # Keresés meglévő mappában
        for folder_id, name in self.folders.items():
            if name == folder_name:
                return folder_id

        # Ha nem létezik, létrehozás
        if folder_name in self.created_folders:
            return self.created_folders[folder_name]

        print(f"  ..'{folder_name}' mappa létrehozása...")
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }

        folder = self.service.files().create(
            body=file_metadata,
            fields='id'
        ).execute()

        folder_id = folder['id']
        self.folders[folder_id] = folder_name
        self.created_folders[folder_name] = folder_id
        print(f"  OK - Létrehozva: {folder_name}")
        return folder_id

    def move_file(self, file_id: str, target_folder_id: str) -> bool:
        """Fájl mozgatása"""
        try:
            # Jelenlegi szülő lekérése
            file_info = self.service.files().get(
                fileId=file_id,
                fields='parents'
            ).execute()

            previous_parents = file_info.get('parents', [])

            # Ha nincs szülő (valódi gyökér fájl), csak hozzáadni
            if not previous_parents:
                self.service.files().update(
                    fileId=file_id,
                    addParents=target_folder_id,
                    fields='id, parents'
                ).execute()
            else:
                # Ha van szülő, kopírozni helyett (megosztott fájlok)
                print(f"      (megosztott fájl - kihagyva)")
                return False

            return True
        except Exception as e:
            print(f"      HIBA: {str(e)}")
            return False

    def organize(self):
        """Fájlok szervezése"""
        print("\n..Gyökér fájlok szervezése...")

        root_files = self.get_root_files()
        if not root_files:
            print("Nincs gyökér fájl!")
            return 0

        # Kategóriák szerinti csoportosítás
        categories = defaultdict(list)

        for file_info in root_files:
            category = self.categorize_file(file_info['name'], file_info['mimeType'])
            categories[category].append(file_info)

        # Szervezés kategóriánként
        moved_count = 0
        for category in sorted(categories.keys()):
            files = categories[category]
            print(f"\n{category} ({len(files)} fájl):")

            # Mappa keresése/létrehozása
            folder_id = self.find_or_create_folder(category)

            # Fájlok mozgatása
            for file_info in files:
                success = self.move_file(file_info['id'], folder_id)
                status = "OK" if success else "HIBA"
                print(f"  [{status}] {file_info['name']}")
                if success:
                    moved_count += 1

        return moved_count


def main():
    print("=" * 80)
    print("GYÖKÉR FÁJLOK SZERVEZÉSE")
    print("=" * 80)

    organizer = RootFileOrganizer()

    # 1. Bejelentkezés
    organizer.authenticate()

    # 2. Fájlok lekérése
    organizer.get_all_files()

    # 3. Szervezés
    moved_count = organizer.organize()

    # 4. Összefoglalás
    print("\n" + "=" * 80)
    print("SZERVEZÉS BEFEJEZVE")
    print("=" * 80)
    print(f"Mozgatott fájlok: {moved_count} db")
    print("=" * 80)


if __name__ == '__main__':
    main()
