#!/usr/bin/env python3
"""
Cisco Catalyst Center - Enterprise Site Finder
Megkeresi az összes Enterprise nevű site-ot a hierarchiában
"""

import requests
import json
import getpass
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_auth_token(host: str, username: str, password: str) -> str:
    """Authentikálódás és token szerzése"""
    url = f"https://{host}/dna/system/api/v1/auth/token"
    response = requests.post(
        url,
        auth=(username, password),
        verify=False,
        timeout=10
    )
    if response.status_code == 200:
        token = response.json().get('Token')
        if token:
            return token
    raise Exception(f"Authentikáció sikertelen: HTTP {response.status_code}")

def get_sites(host: str, token: str):
    """Lekérdezi az összes site-ot"""
    headers = {
        'X-Auth-Token': token,
        'Content-Type': 'application/json'
    }

    # Próbálj több endpoint-ot
    endpoints = [
        "/dna/intent/api/v1/sites",
        "/dna/intent/api/v1/site-hierarchy",
        "/dna/intent/api/v2/sites",
    ]

    for endpoint in endpoints:
        try:
            url = f"https://{host}{endpoint}"
            print(f"[*] Próbálkozás: {endpoint}")
            response = requests.get(url, headers=headers, verify=False, timeout=10)

            if response.status_code == 200:
                data = response.json()
                print(f"[✓] Sikeres lekérdezés: {endpoint}")
                print(f"\n[*] RAW RESPONSE (első 500 kar):")
                print(json.dumps(data, indent=2)[:1000])
                print("\n" + "="*70 + "\n")
                return data, endpoint
            else:
                print(f"    [!] HTTP {response.status_code}\n")
        except Exception as e:
            print(f"    [!] Hiba: {str(e)}\n")

    raise Exception("Nem sikerült lekérdezni a site-okat")

def parse_sites_dynamic(data):
    """Dinamikusan feldolgozza a site adatokat"""
    sites = []

    # Ha "response" kulcs van, azt használjuk
    if isinstance(data, dict):
        site_list = data.get('response', data)
    else:
        site_list = data

    # Ha nem list, de van rá konvertálható
    if not isinstance(site_list, list):
        site_list = [site_list]

    # Feldolgozz minden site-ot
    for item in site_list:
        if not isinstance(item, dict):
            continue

        # Próbáld meg az összes lehetséges field-et
        site_info = {
            'id': item.get('id') or item.get('siteId') or item.get('site_id'),
            'name': item.get('name') or item.get('siteName') or item.get('site_name'),
            'hierarchy': item.get('siteNameHierarchy') or item.get('nameHierarchy') or item.get('hierarchy'),
            'parent_id': item.get('parentId') or item.get('parent_id'),
            'full_item': item  # Az egész objektum debugging-hoz
        }

        # Ha van név vagy hierarchy, add hozzá
        if site_info['name'] or site_info['hierarchy']:
            sites.append(site_info)

    return sites

def main():
    print("="*70)
    print("Cisco Catalyst Center - Enterprise Site Finder")
    print("="*70 + "\n")

    host = "10.8.11.100"
    username = "admin"

    password = getpass.getpass("Jelszó: ")

    try:
        # 1. Authentikáció
        print("[*] Authentikálódás...")
        token = get_auth_token(host, username, password)
        print("[✓] Sikeres authentikáció!\n")

        # 2. Site-ok lekérdezése
        print("[*] Site-ok lekérdezése...\n")
        data, endpoint = get_sites(host, token)

        # 3. Site-ok feldolgozása
        print("[*] Site-ok feldolgozása...\n")
        sites = parse_sites_dynamic(data)

        print(f"[✓] {len(sites)} site feldolgozva\n")
        print("="*70)
        print("ÖSSZES SITE")
        print("="*70 + "\n")

        # 4. Kiírás
        enterprise_sites = []

        for i, site in enumerate(sites, 1):
            print(f"[{i}] SITE INFORMÁCIÓ:")
            print(f"    ID: {site['id']}")
            print(f"    Név: {site['name']}")
            print(f"    Hierarchia: {site['hierarchy']}")
            print(f"    Parent ID: {site['parent_id']}")

            # Teljes objektum a debuggoláshoz
            if site['full_item']:
                print(f"\n    TELJES OBJEKTUM:")
                for key, value in site['full_item'].items():
                    if key not in ['children', 'payload']:  # Skip nagy objektumok
                        print(f"        {key}: {value}")

            # Keress "Enterprise" szó-t
            site_name_str = str(site['name']).lower() if site['name'] else ""
            site_hierarchy_str = str(site['hierarchy']).lower() if site['hierarchy'] else ""

            if 'enterprise' in site_name_str or 'enterprise' in site_hierarchy_str:
                enterprise_sites.append(site)
                print("\n    ⭐ ENTERPRISE SITE TALÁLT!")

            print()

        # 5. Enterprise site-ok összefoglalása
        print("\n" + "="*70)
        print(f"ENTERPRISE SITE-OK ({len(enterprise_sites)} talált)")
        print("="*70 + "\n")

        if enterprise_sites:
            for site in enterprise_sites:
                print(f"📍 {site['hierarchy'] or site['name']}")
                print(f"   ID: {site['id']}\n")
        else:
            print("[!] Nincs Enterprise nevű site.\n")

        # 6. Javasolt útvonal
        print("="*70)
        print("JAVASOLT BEÁLLÍTÁS")
        print("="*70 + "\n")

        if enterprise_sites:
            site = enterprise_sites[0]
            hierarchy = site['hierarchy'] or site['name']
            print(f"Az alábbi site-ot használd az IP pool reserválásához:\n")
            print(f"site_hierarchy = \"{hierarchy}\"")
            print(f"site_id = \"{site['id']}\"")
        else:
            print("[!] Nem találtam Enterprise site-ot.")
            print("Válaszd ki az alábbiak közül:\n")
            for site in sites[:10]:
                print(f"  - {site['hierarchy'] or site['name']}")

    except Exception as e:
        print(f"\n[✗] Hiba: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
