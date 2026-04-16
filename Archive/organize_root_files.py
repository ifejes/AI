#!/usr/bin/env python3
"""
Google Drive - Gyökér mappa fájljainak szervezése
Elemzi és javaslatot tesz a gyökér mappában lévő fájlok csoportosítására
"""

import os
from typing import Dict, List, Tuple
from difflib import SequenceMatcher
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
        self.root_files = []

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
            fields='files(id, name, mimeType, parents, webViewLink)',
            pageSize=1000
        ).execute()

        files = results.get('files', [])

        for file in files:
            self.files_cache[file['id']] = file
            if file['mimeType'] == 'application/vnd.google-apps.folder':
                self.folders[file['id']] = file['name']

        print(f"OK - Összesen {len(files)} fájl/mappa")

    def find_root_files(self):
        """Megtalálja a gyökér mappában lévő fájlokat"""
        print("\n..Gyökér mappa fájljainak keresése...")

        for file_id, file_info in self.files_cache.items():
            # Ha nincs parent vagy nincs 'parents' kulcs, az root fájl
            if 'parents' not in file_info or not file_info['parents']:
                # Mappa-e?
                if file_info['mimeType'] != 'application/vnd.google-apps.folder':
                    self.root_files.append(file_info)

        print(f"OK - {len(self.root_files)} gyökér fájl található")
        return self.root_files

    def categorize_files(self) -> Dict[str, List]:
        """Fájlok kategorizálása típus és név alapján"""
        print("\n..Fájlok kategorizálása...")

        categories = {
            'images': [],
            'documents': [],
            'audio': [],
            'video': [],
            'archives': [],
            'other': []
        }

        mime_type_map = {
            'image': 'images',
            'audio': 'audio',
            'video': 'video',
            'pdf': 'documents',
            'document': 'documents',
            'spreadsheet': 'documents',
            'presentation': 'documents',
            'archive': 'archives',
            'zip': 'archives',
            'rar': 'archives',
        }

        for file_info in self.root_files:
            mime = file_info['mimeType'].lower()
            name = file_info['name'].lower()
            categorized = False

            # MIME type alapján
            for key, category in mime_type_map.items():
                if key in mime:
                    categories[category].append(file_info)
                    categorized = True
                    break

            # Fájlnév alapján (ha mime nem segít)
            if not categorized:
                for key, category in mime_type_map.items():
                    if key in name:
                        categories[category].append(file_info)
                        categorized = True
                        break

            # Alapértelmezett
            if not categorized:
                categories['other'].append(file_info)

        return categories

    def find_best_folder(self, file_name: str, file_mime: str, category: str) -> Tuple[str, str]:
        """Meghatározza az ideális mappát a fájlnak"""
        # Heurisztika a mappa kiválasztásához
        name_lower = file_name.lower()

        # Keresés kategóriavá nevű mappákban
        category_map = {
            'images': ['Images', 'Képek', 'Photos', 'Fotók', 'Pictures'],
            'documents': ['Documents', 'Dokumentumok', 'Docs', 'Papers'],
            'audio': ['Music', 'Audio', 'Audiobook', 'Zene', 'Audiokönyv'],
            'video': ['Videos', 'Videók', 'Movies', 'Filmek'],
            'archives': ['Archives', 'Archives', 'Zip'],
        }

        # Keresés az ismert mappák között
        for folder_id, folder_name in self.folders.items():
            folder_name_lower = folder_name.lower()

            # Kategória alapján
            if category in category_map:
                for pattern in category_map[category]:
                    if pattern.lower() in folder_name_lower:
                        return folder_id, folder_name

            # Fájlnév alapján
            if category == 'other':
                # Keresünk olyan mappákat, amely hasonlít a fájlnév első szavára
                first_word = name_lower.split()[0] if name_lower.split() else ""
                if first_word and len(first_word) > 3:
                    if first_word in folder_name_lower or folder_name_lower in first_word:
                        return folder_id, folder_name

        # Ha nincs találat, javaslatunk egy új mappát
        if category != 'other':
            suggested_name = category.replace('_', ' ').title()
        else:
            first_word = file_name.split()[0] if file_name.split() else "Other"
            suggested_name = first_word

        return None, f"[UJ MAPPA] {suggested_name}"

    def generate_report(self):
        """Szervezési javaslat generálása"""
        print("\n..Javaslat generálása...")

        categories = self.categorize_files()

        report = "=" * 80 + "\n"
        report += "GYÖKÉR MAPPA FÁJLJAINAK SZERVEZÉSI JAVASLATA\n"
        report += "=" * 80 + "\n\n"

        organization_plan = {}

        for category, files in categories.items():
            if not files:
                continue

            report += f"\n{category.upper()} ({len(files)} fájl)\n"
            report += "-" * 80 + "\n"

            for file_info in files:
                file_name = file_info['name']
                file_id = file_info['id']
                folder_id, suggested_folder = self.find_best_folder(
                    file_name, file_info['mimeType'], category)

                report += f"  • {file_name}\n"
                report += f"    ID: {file_id}\n"

                if folder_id:
                    report += f"    Mozgat: {suggested_folder}\n"
                else:
                    report += f"    Javasolt: {suggested_folder}\n"

                organization_plan[file_id] = {
                    'name': file_name,
                    'folder_id': folder_id,
                    'suggested_folder': suggested_folder,
                    'category': category
                }

        report += "\n" + "=" * 80 + "\n"
        report += "SZERVEZÉSI TERV MENTVE: root_organization_plan.json\n"
        report += "=" * 80 + "\n"

        return report, organization_plan

    def print_summary(self, categories: Dict[str, List]):
        """Összefoglalás kiírása"""
        print("\n" + "=" * 80)
        print("GYÖKÉR MAPPA ANALÍZISE")
        print("=" * 80)
        for category, files in categories.items():
            if files:
                print(f"  {category.upper()}: {len(files)} fájl")
        print("=" * 80)


def main():
    print("=" * 80)
    print("GYÖKÉR MAPPA SZERVEZÉSI ANALÍZIS")
    print("=" * 80)

    organizer = RootFileOrganizer()

    # 1. Bejelentkezés
    organizer.authenticate()

    # 2. Fájlok lekérése
    organizer.get_all_files()

    # 3. Gyökér fájlok keresése
    root_files = organizer.find_root_files()

    if not root_files:
        print("\n✓ Nincs gyökér mappában lévő fájl!")
        return

    # 4. Kategorizálás
    categories = organizer.categorize_files()
    organizer.print_summary(categories)

    # 5. Javaslat generálása
    report, organization_plan = organizer.generate_report()
    print(report)

    # 6. Terv mentése
    import json
    with open('root_organization_plan.json', 'w', encoding='utf-8') as f:
        json.dump(organization_plan, f, ensure_ascii=False, indent=2)

    print("✓ Javaslat mentve: root_organization_plan.json")


if __name__ == '__main__':
    main()
