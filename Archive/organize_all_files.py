#!/usr/bin/env python3
"""
Google Drive - Összes fájl szervezése kategóriák szerint
"""

import os
from typing import Dict, List, Tuple
from collections import defaultdict

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive']


class FileOrganizer:
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

    def find_or_create_folder(self, folder_name: str, parent_id: str = None) -> str:
        """Mappa keresése vagy létrehozása"""
        # Keresés meglévő mappában
        for folder_id, name in self.folders.items():
            if name == folder_name and self.is_in_parent(folder_id, parent_id):
                return folder_id

        # Ha nem létezik, létrehozás
        if folder_name in self.created_folders:
            return self.created_folders[folder_name]

        print(f"    ..'{folder_name}' mappa létrehozása...")
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            file_metadata['parents'] = [parent_id]

        folder = self.service.files().create(
            body=file_metadata,
            fields='id'
        ).execute()

        folder_id = folder['id']
        self.folders[folder_id] = folder_name
        self.created_folders[folder_name] = folder_id
        print(f"    OK - Létrehozva: {folder_name}")
        return folder_id

    def is_in_parent(self, folder_id: str, parent_id: str = None) -> bool:
        """Ellenőrzi, hogy a mappa a szülő mappában van-e"""
        if parent_id is None:
            return True
        if folder_id not in self.files_cache:
            return False
        parents = self.files_cache[folder_id].get('parents', [])
        return parent_id in parents

    def move_file(self, file_id: str, target_folder_id: str) -> bool:
        """Fájl mozgatása"""
        try:
            # Jelenlegi szülő lekérése
            file_info = self.service.files().get(
                fileId=file_id,
                fields='parents'
            ).execute()

            previous_parents = ",".join(file_info.get('parents', []))

            # Mozgatás
            self.service.files().update(
                fileId=file_id,
                addParents=target_folder_id,
                removeParents=previous_parents,
                fields='id, parents'
            ).execute()

            return True
        except Exception as e:
            print(f"        HIBA mozgatáskor: {str(e)}")
            return False

    def organize_files(self):
        """Összes fájl szervezése"""
        print("\n..Fájlok szervezése...")

        # Kategóriák szerinti csoportosítás
        categories = defaultdict(list)

        for file_id, file_info in self.files_cache.items():
            # Mappákat kihagyni
            if file_info['mimeType'] == 'application/vnd.google-apps.folder':
                continue

            category = self.categorize_file(file_info['name'], file_info['mimeType'])
            categories[category].append((file_id, file_info['name']))

        # Szervezés kategóriánként
        moved_count = 0
        for category, files in categories.items():
            print(f"\n{category} ({len(files)} fájl):")

            # Mappa keresése/létrehozása
            folder_id = self.find_or_create_folder(category)

            # Fájlok mozgatása
            for file_id, file_name in files:
                success = self.move_file(file_id, folder_id)
                status = "OK" if success else "HIBA"
                print(f"  [{status}] {file_name}")
                if success:
                    moved_count += 1

        return moved_count

    def print_summary(self, moved_count: int):
        """Összefoglalás"""
        print("\n" + "=" * 80)
        print("SZERVEZÉS BEFEJEZVE")
        print("=" * 80)
        print(f"Mozgatott fájlok: {moved_count} db")
        print("=" * 80)


def main():
    print("=" * 80)
    print("GOOGLE DRIVE - FÁJLOK SZERVEZÉSE")
    print("=" * 80)

    organizer = FileOrganizer()

    # 1. Bejelentkezés
    organizer.authenticate()

    # 2. Fájlok lekérése
    organizer.get_all_files()

    # 3. Szervezés
    moved_count = organizer.organize_files()

    # 4. Összefoglalás
    organizer.print_summary(moved_count)


if __name__ == '__main__':
    main()
