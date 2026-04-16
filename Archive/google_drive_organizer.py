#!/usr/bin/env python3
"""
Google Drive Organizer
Elemzi és javaslatot tesz a Google Drive tartalom átszervezésére
"""

import os
import json
import hashlib
from typing import Dict, List, Tuple
from difflib import SequenceMatcher
from collections import defaultdict

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

SCOPES = ['https://www.googleapis.com/auth/drive']


class GoogleDriveOrganizer:
    def __init__(self):
        self.service = None
        self.files_cache = {}  # {file_id: {name, parents, mimeType, hash}}
        self.folders = {}  # {folder_id: folder_name}

    def authenticate(self):
        """Bejelentkezés OAuth2.0-val"""
        creds = None

        # Token fájl betöltése, ha létezik
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)

        # Ha nincs valid token, új loginprocess
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)

            # Token mentése későbbi használathoz
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        self.service = build('drive', 'v3', credentials=creds)
        print("✓ Bejelentkezés sikeres")

    def get_all_files(self):
        """Lekéri az összes fájlt és mappát a Drive-ról"""
        print("\n📂 Fájlok lekérése...")

        query = "trashed = false"
        results = self.service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name, mimeType, parents, size)',
            pageSize=1000
        ).execute()

        files = results.get('files', [])

        # Mappák mentése
        for file in files:
            if file['mimeType'] == 'application/vnd.google-apps.folder':
                self.folders[file['id']] = file['name']

        self.files_cache = {f['id']: f for f in files}
        print(f"✓ Összesen {len(files)} fájl/mappa találva")
        return files

    def calculate_file_hash(self, file_id: str) -> str:
        """Fájl MD5 hash-ének kiszámítása"""
        try:
            request = self.service.files().get_media(fileId=file_id)
            file = io.BytesIO()
            downloader = MediaIoBaseDownload(file, request)

            md5 = hashlib.md5()
            done = False
            while not done:
                status, done = downloader.next_chunk()
                file.seek(0)
                md5.update(file.read())

            return md5.hexdigest()
        except Exception as e:
            return None

    def find_duplicates(self) -> Dict[str, List]:
        """Duplikátumok keresése (azonos név/hash)"""
        print("\n🔍 Duplikátumok keresése...")

        duplicates_by_name = defaultdict(list)
        duplicates_by_hash = defaultdict(list)

        # Duplikátumok név alapján
        for file_id, file_info in self.files_cache.items():
            if file_info['mimeType'] != 'application/vnd.google-apps.folder':
                name = file_info['name']
                duplicates_by_name[name].append(file_id)

        # Szűrés: csak azok, amelyek többszörös előfordulásban vannak
        duplicates_by_name = {
            name: ids for name, ids in duplicates_by_name.items()
            if len(ids) > 1
        }

        print(f"✓ Név alapján {len(duplicates_by_name)} duplikátum-csoport találva")

        return {
            'by_name': duplicates_by_name,
            'groups': []
        }

    def find_similar_files(self, threshold: float = 0.7) -> Dict[str, List]:
        """Hasonló fájlnevek keresése"""
        print("\n🔗 Hasonló fájlok keresése...")

        file_list = [
            (fid, info) for fid, info in self.files_cache.items()
            if info['mimeType'] != 'application/vnd.google-apps.folder'
        ]

        similar_groups = []
        processed = set()

        for i, (fid1, info1) in enumerate(file_list):
            if fid1 in processed:
                continue

            group = [fid1]
            name1 = info1['name'].lower()

            for fid2, info2 in file_list[i+1:]:
                if fid2 in processed:
                    continue

                name2 = info2['name'].lower()
                similarity = SequenceMatcher(None, name1, name2).ratio()

                if similarity >= threshold:
                    group.append(fid2)
                    processed.add(fid2)

            if len(group) > 1:
                similar_groups.append(group)
                processed.add(fid1)

        print(f"✓ {len(similar_groups)} hasonló-csoport találva")
        return similar_groups

    def generate_report(self) -> str:
        """Átszervezési javaslat generálása"""
        print("\n📋 Javaslat generálása...")

        duplicates = self.find_duplicates()
        similar_groups = self.find_similar_files()

        report = "=" * 80 + "\n"
        report += "GOOGLE DRIVE ÁTSZERVEZÉSI JAVASLAT\n"
        report += "=" * 80 + "\n\n"

        # Duplikátumok
        report += "1️⃣  DUPLIKÁTUMOK (Törlésre jelöltek)\n"
        report += "-" * 80 + "\n"

        if duplicates['by_name']:
            for name, file_ids in duplicates['by_name'].items():
                report += f"\n📄 '{name}' - {len(file_ids)} másolat:\n"
                for file_id in file_ids:
                    file_info = self.files_cache[file_id]
                    parent_name = self._get_parent_name(file_info.get('parents', [None])[0])
                    report += f"   • {file_id}\n"
                    report += f"     Hely: {parent_name}\n"
                    report += f"     Méret: {self._format_size(file_info.get('size', 0))}\n"
                report += f"   ✓ Javaslatom: Az 1. másolat megtartása, a többi törlése\n"
        else:
            report += "   ✓ Nincs duplikátum\n"

        # Hasonló tartalmak
        report += "\n\n2️⃣  HASONLÓ TARTALMAK (Csoportosítandók)\n"
        report += "-" * 80 + "\n"

        if similar_groups:
            for idx, group in enumerate(similar_groups, 1):
                report += f"\n📁 Csoport #{idx}:\n"
                names = []
                for file_id in group:
                    file_info = self.files_cache[file_id]
                    names.append(file_info['name'])
                    parent_name = self._get_parent_name(file_info.get('parents', [None])[0])
                    report += f"   • {file_info['name']}\n"
                    report += f"     Hely: {parent_name}\n"

                # Javasolt mappanév
                common_name = self._find_common_prefix(names)
                report += f"   ✓ Javasolt mappa: '{common_name}'\n"
        else:
            report += "   ✓ Nincs szükség csoportosításra\n"

        report += "\n" + "=" * 80 + "\n"
        report += "KÖVETKEZŐ LÉPÉSEK:\n"
        report += "1. Ellenőrizd a javaslatokat\n"
        report += "2. Módosítsd a javaslat fájlt (organize_plan.json)\n"
        report += "3. Futtasd az 'apply_plan.py' scriptet a végrehajtáshoz\n"
        report += "=" * 80 + "\n"

        return report

    def _get_parent_name(self, parent_id: str) -> str:
        """Szülőmappa nevének lekérése"""
        if not parent_id:
            return "Gyökér"
        return self.folders.get(parent_id, "Ismeretlen")

    def _format_size(self, size) -> str:
        """Fájlméret formázása"""
        if not size or size == '0':
            return "?"
        size = int(size) if isinstance(size, str) else size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def _find_common_prefix(self, names: List[str]) -> str:
        """Közös előtag keresése fájlnevekben"""
        if not names:
            return "Új mappa"

        # Szavak közös előtagja
        words = [n.split()[0] for n in names]
        common = words[0].split('_')[0]

        for word in words[1:]:
            word_prefix = word.split('_')[0]
            if not word_prefix.startswith(common):
                common = common[:len(common)-1]

        return common or "Hasonló fájlok"


def main():
    organizer = GoogleDriveOrganizer()

    # 1. Bejelentkezés
    print("🚀 Google Drive Organizer indítása...")
    organizer.authenticate()

    # 2. Fájlok lekérése
    organizer.get_all_files()

    # 3. Javaslat generálása
    report = organizer.generate_report()
    print(report)

    # 4. Javaslat mentése fájlba
    with open('organize_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)

    print("✓ Javaslat mentve: organize_report.txt")


if __name__ == '__main__':
    main()
