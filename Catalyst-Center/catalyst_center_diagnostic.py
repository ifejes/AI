#!/usr/bin/env python3
"""
Cisco Catalyst Center Diagnostikai Tool
Segítség az authentikálási és API problémák diagnosztizálásához
"""

import requests
import json
import getpass
import sys
import urllib3
import base64
from urllib.parse import urljoin

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class CatalystCenterDiagnostic:
    """Diagnosztikai eszköz a CC API-hoz"""

    def __init__(self, host: str):
        self.host = host
        self.base_url = f"https://{host}"
        self.api_v1_url = f"{self.base_url}/dna/intent/api/v1"
        self.api_v2_url = f"{self.base_url}/dna/intent/api/v2"
        self.session = requests.Session()

    def test_connectivity(self) -> bool:
        """Tesztel a kapcsolódást a CC-hez"""
        print("[*] 1. HÁLÓZATI KAPCSOLAT TESZTELÉSE")
        print("-" * 70)

        try:
            response = self.session.get(
                self.base_url,
                verify=False,
                timeout=5
            )
            print(f"[✓] CC elérhető: {self.host}")
            print(f"    HTTP Status: {response.status_code}")
            return True
        except requests.exceptions.ConnectionError:
            print(f"[✗] Nem lehet csatlakozni: {self.host}")
            return False
        except Exception as e:
            print(f"[✗] Hiba: {str(e)}")
            return False

    def test_basic_auth(self, username: str, password: str) -> bool:
        """Tesztel a Basic Auth-ot"""
        print("\n[*] 2. BASIC AUTH TESZTELÉSE")
        print("-" * 70)

        try:
            # Basic Auth credentials
            credentials = f"{username}:{password}"
            encoded = base64.b64encode(credentials.encode()).decode()

            print(f"[*] Felhasználónév: {username}")
            print(f"[*] Jelszó: {'*' * len(password)}")
            print(f"[*] Base64 Encoded: {encoded[:20]}...")

            # Test 1: HELYES endpoint - /dna/system/api/v1/auth/token
            print("\n[*] Test 1: /dna/system/api/v1/auth/token (HELYES ENDPOINT)")
            url = f"{self.base_url}/dna/system/api/v1/auth/token"
            response = self.session.post(
                url,
                auth=(username, password),
                verify=False,
                timeout=5
            )

            print(f"    HTTP Status: {response.status_code}")

            if response.status_code == 200:
                token = response.json().get('Token')
                if token:
                    print(f"[✓] Basic Auth sikeres! Token szerzett.")
                    return True
                else:
                    print(f"[!] HTTP 200 de Token nincs")
            else:
                print(f"[!] HTTP {response.status_code}")
                print(f"    Válasz: {response.text[:200]}")

            # Test 2: Alternatív - API v1 intent
            print("\n[*] Test 2: /dna/intent/api/v1/auth/token (ALTERNATÍV)")
            url = f"{self.api_v1_url}/auth/token"
            response = self.session.post(
                url,
                auth=(username, password),
                verify=False,
                timeout=5
            )

            print(f"    HTTP Status: {response.status_code}")

            if response.status_code == 200:
                print(f"[✓] Basic Auth sikeres (intent v1)!")
                return True
            else:
                print(f"[!] HTTP {response.status_code}")

            # Test 3: API v2
            print("\n[*] Test 3: /dna/intent/api/v2/auth/token (ALTERNATÍV)")
            url = f"{self.api_v2_url}/auth/token"
            response = self.session.post(
                url,
                auth=(username, password),
                verify=False,
                timeout=5
            )

            print(f"    HTTP Status: {response.status_code}")

            if response.status_code == 200:
                print(f"[✓] Basic Auth sikeres (intent v2)!")
                return True
            else:
                print(f"[!] HTTP {response.status_code}")

            return False

        except Exception as e:
            print(f"[✗] Hiba: {str(e)}")
            return False

    def test_header_auth(self, username: str, password: str) -> bool:
        """Tesztel a Header-alapú Auth-ot"""
        print("\n[*] 3. HEADER-ALAPÚ AUTH TESZTELÉSE")
        print("-" * 70)

        try:
            # JSON body-ban küldött credentials
            headers = {
                'Content-Type': 'application/json'
            }

            payload = {
                'username': username,
                'password': password
            }

            print(f"[*] POST body-ban küldött credentials")

            url = f"{self.api_v1_url}/auth/token"
            response = self.session.post(
                url,
                json=payload,
                headers=headers,
                verify=False,
                timeout=5
            )

            print(f"    HTTP Status: {response.status_code}")

            if response.status_code == 200:
                print(f"[✓] Header Auth sikeres!")
                print(f"    Válasz: {response.json()}")
                return True
            else:
                print(f"[!] HTTP {response.status_code}")
                print(f"    Válasz: {response.text[:200]}")

            return False

        except Exception as e:
            print(f"[✗] Hiba: {str(e)}")
            return False

    def get_catalyst_center_version(self) -> str:
        """Lekérdezi a CC verzióját"""
        print("\n[*] 4. CATALYST CENTER VERZIÓ LEKÉRDEZÉSE")
        print("-" * 70)

        try:
            # Próbáld meg a /api/v1/system/version endpoint-ot
            endpoints = [
                f"{self.api_v1_url}/system/version",
                f"{self.api_v2_url}/system/version",
                f"{self.base_url}/api/v1/system/version",
                f"{self.base_url}/api/system/version",
            ]

            for url in endpoints:
                try:
                    response = self.session.get(url, verify=False, timeout=3)
                    if response.status_code == 200:
                        print(f"[✓] Verzió lekérdezve: {url}")
                        print(f"    {response.json()}")
                        return response.json()
                except:
                    pass

            print("[!] Verzió nem érhető el")
            return None

        except Exception as e:
            print(f"[✗] Hiba: {str(e)}")
            return None

    def test_site_query(self, token: str) -> bool:
        """Tesztel a site-ok lekérdezését (ezután auth szükséges)"""
        print("\n[*] 5. SITE-OK LEKÉRDEZÉSÉNEK TESZTELÉSE")
        print("-" * 70)

        if not token:
            print("[!] Token nincs, skip...")
            return False

        try:
            headers = {
                'X-Auth-Token': token,
                'Content-Type': 'application/json'
            }

            url = f"{self.api_v1_url}/sites"
            response = self.session.get(url, headers=headers, verify=False, timeout=5)

            print(f"[*] GET {url}")
            print(f"    HTTP Status: {response.status_code}")

            if response.status_code == 200:
                sites = response.json().get('response', [])
                print(f"[✓] {len(sites)} site találva")
                for site in sites[:5]:  # Első 5 site
                    print(f"    - {site.get('siteNameHierarchy')}")
                return True
            else:
                print(f"[!] HTTP {response.status_code}")
                print(f"    Válasz: {response.text[:200]}")
                return False

        except Exception as e:
            print(f"[✗] Hiba: {str(e)}")
            return False

    def print_recommendations(self):
        """Nyomtat ajánlásokat"""
        print("\n" + "=" * 70)
        print("AJÁNLÁSOK")
        print("=" * 70)

        recommendations = [
            "1. Ellenőrizd az admin jelszót - biztosan helyesen gépelted-e be?",
            "2. Az LDAP/AD authentikáció használat a CC-ben?",
            "   → Ha igen, az admin felhasználó LDAP-os felhasználó-e?",
            "3. A CC rendszere korlátozza az API hozzáférést?",
            "   → Admin felület → System → User & Role Management",
            "4. Próbálkozz meg az alábbi Catalyst Center verzióval:",
            "   → CC 2.2, 2.3, 2.4 - eltérő API-k lehetnek",
            "5. A jelszó tartalmaz-e speciális karaktereket?",
            "   → Pl. @, !, $, % - ezek előfordulhat, hogy escapel kell",
            "6. SSL tanúsítvány problémái?",
            "   → Próbáld meg a verify_ssl=True opciót",
            "7. Proxy vagy firewall közvetül van?",
            "   → Ellenőrizd a hálózati szabályokat",
        ]

        for rec in recommendations:
            print(f"[!] {rec}")


def main():
    print("=" * 70)
    print("Cisco Catalyst Center Diagnostikai Tool")
    print("=" * 70)
    print()

    # Input
    catalyst_center_ip = "10.8.11.100"
    username = "admin"

    print(f"Catalyst Center IP: {catalyst_center_ip}")
    print(f"Felhasználónév: {username}")

    password = getpass.getpass("Jelszó: ")

    if not password:
        print("[✗] Hiba: Jelszó nem adható meg üres értékkel!")
        sys.exit(1)

    # Diagnostic tool inicializálása
    diag = CatalystCenterDiagnostic(catalyst_center_ip)

    # Tesztek futtatása
    print("\n")

    # Test 1: Hálózati kapcsolat
    if not diag.test_connectivity():
        print("\n[✗] Nem lehet csatlakozni a CC-hez!")
        print("[!] Ellenőrizd az IP cím és a hálózati kapcsolat!")
        sys.exit(1)

    # Test 2: Basic Auth
    if not diag.test_basic_auth(username, password):
        print("\n[!] Basic Auth nem működött, próbálkozunk header auth-tal...")
        if not diag.test_header_auth(username, password):
            print("\n[✗] Egyik authentikálási módszer sem működött!")
            diag.print_recommendations()
            sys.exit(1)

    # Test 3: Verzió
    diag.get_catalyst_center_version()

    # Test 4: Site-ok (csak ha van token)
    # Ez több information-t adna, de most kihagyjuk

    print("\n" + "=" * 70)
    print("DIAGNÓZIS BEFEJEZVE")
    print("=" * 70)

    print("\n[✓] Az authentikáció sikeres!")
    print("[✓] Mostmár futtathatod az eredeti scriptet:")
    print("    python catalyst_center_ip_pool_reservation.py")


if __name__ == "__main__":
    main()
