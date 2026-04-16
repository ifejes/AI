#!/usr/bin/env python3
"""
Google Drive Organizer - Execution
Végrehajtja az átszervezést: duplikátumok törlése
"""

import os
from typing import Dict, List
from collections import defaultdict
from difflib import SequenceMatcher

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive']


class GoogleDriveExecutor:
    def __init__(self):
        self.service = None
        self.files_cache = {}
        self.folders = {}
        self.deleted_count = 0
        self.deleted_size = 0

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
        print("..Fájlok lekérése...")

        query = "trashed = false"
        results = self.service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name, mimeType, parents, size)',
            pageSize=1000
        ).execute()

        files = results.get('files', [])

        for file in files:
            if file['mimeType'] == 'application/vnd.google-apps.folder':
                self.folders[file['id']] = file['name']

        self.files_cache = {f['id']: f for f in files}
        print(f"OK - Összesen {len(files)} fájl/mappa")

    def find_duplicates_to_delete(self) -> List[str]:
        """Meghatározza, mely duplikátumokat kell törölni"""
        print("\n..Duplikátumok azonosítása...")

        duplicates_by_name = defaultdict(list)

        for file_id, file_info in self.files_cache.items():
            if file_info['mimeType'] != 'application/vnd.google-apps.folder':
                name = file_info['name']
                duplicates_by_name[name].append(file_id)

        # Szűrés: csak azok, amelyek többszörös előfordulásban vannak
        duplicates_by_name = {
            name: ids for name, ids in duplicates_by_name.items()
            if len(ids) > 1
        }

        to_delete = []
        for name, file_ids in duplicates_by_name.items():
            # Az első másolat megtartása, a többi törlésre jelölve
            for file_id in file_ids[1:]:
                to_delete.append(file_id)

        print(f"OK - {len(to_delete)} fájl jelölt törlésre")
        return to_delete

    def delete_files(self, file_ids: List[str]):
        """Fájlok törlése Google Drive-ról"""
        print(f"\nFájlok törlése ({len(file_ids)} db)...")

        for i, file_id in enumerate(file_ids, 1):
            file_info = self.files_cache[file_id]
            file_name = file_info['name']
            file_size = int(file_info.get('size', 0))

            try:
                self.service.files().delete(fileId=file_id).execute()
                self.deleted_count += 1
                self.deleted_size += file_size
                print(f"  [{i}/{len(file_ids)}] TÖRÖLVE: {file_name}")
            except Exception as e:
                print(f"  [{i}/{len(file_ids)}] HIBA: {file_name} - {str(e)}")

    def format_size(self, size: int) -> str:
        """Fájlméret formázása"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def print_summary(self):
        """Összefoglalás kiírása"""
        print("\n" + "=" * 80)
        print("ÁTSZERVEZÉS BEFEJEZVE")
        print("=" * 80)
        print(f"Törolt fájlok: {self.deleted_count} db")
        print(f"Felszabadított hely: {self.format_size(self.deleted_size)}")
        print("=" * 80)


def main():
    print("=" * 80)
    print("GOOGLE DRIVE ORGANIZER - VÉGREHAJTÁS")
    print("=" * 80)
    print()

    executor = GoogleDriveExecutor()

    # 1. Bejelentkezés
    executor.authenticate()

    # 2. Fájlok lekérése
    executor.get_all_files()

    # 3. Duplikátumok azonosítása
    to_delete = executor.find_duplicates_to_delete()

    if not to_delete:
        print("\nNincs mit törölni!")
        return

    # 4. Törlés
    executor.delete_files(to_delete)

    # 6. Összefoglalás
    executor.print_summary()

    print("\nKesz!")


if __name__ == '__main__':
    main()
