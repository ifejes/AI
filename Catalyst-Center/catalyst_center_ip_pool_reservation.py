#!/usr/bin/env python3
"""
Cisco Catalyst Center IP Pool Reservation Script
Szerzője: AI Assistant
Funkció: IP pool (10.110.4.0/24) reserválása a Global/Hungary/Budapest/Enterprise site-hoz
"""

import requests
import json
import getpass
import sys
import urllib3
from typing import Optional, Dict, Any

# SSL warning elnyomása (self-signed tanúsítvány)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class CatalystCenterAPI:
    """
    Catalyst Center REST API kliens
    """

    def __init__(self, host: str, username: str, password: str, verify_ssl: bool = False):
        """
        Inicializálás

        Args:
            host: Catalyst Center IP cím vagy hostname
            username: Felhasználónév
            password: Jelszó
            verify_ssl: SSL tanúsítvány ellenőrzése (alapértelmezetten kikapcsolt)
        """
        self.host = host
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.base_url = f"https://{host}/dna/intent/api/v1"
        self.token = None
        self.session = requests.Session()

    def authenticate(self) -> bool:
        """
        Authentikálódás a Catalyst Center-hez
        Az /dna/system/api/v1/auth/token endpoint-ot használja (a helyes!)

        Returns:
            bool: True ha sikeres, False ha hiba
        """
        try:
            print("[*] Csatlakozás a Catalyst Center-hez...")

            # A HELYES endpoint: /dna/system/api/v1/auth/token
            auth_url = f"https://{self.host}/dna/system/api/v1/auth/token"
            print(f"[*] Auth URL: {auth_url}")

            # Basic Auth (RFC 7617)
            print(f"[*] Authentikálás...")
            response = self.session.post(
                auth_url,
                auth=(self.username, self.password),
                verify=self.verify_ssl,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                self.token = data.get('Token')

                if self.token:
                    print(f"[✓] Sikeres authentikáció!")
                    # Az API v1 endpoint beállítása
                    self.base_url = f"https://{self.host}/dna/intent/api/v1"
                    # Token hozzáadása a session-höz
                    self.session.headers.update({
                        'X-Auth-Token': self.token,
                        'Content-Type': 'application/json'
                    })
                    return True
                else:
                    print(f"[✗] Hiba: HTTP 200 de Token nincs a válaszban")
                    print(f"    Válasz: {response.text}")
                    return False
            else:
                print(f"[✗] Authentikálási hiba: HTTP {response.status_code}")
                print(f"    Válasz: {response.text}")
                return False

        except requests.exceptions.ConnectionError:
            print(f"[✗] Kapcsolódási hiba: {self.host} nem elérhető")
            print(f"    Ellenőrizd az IP cím és a hálózati kapcsolat!")
            return False
        except requests.exceptions.Timeout:
            print(f"[✗] Timeout: A Catalyst Center nem válaszol")
            print(f"    Ellenőrizd a hálózati kapcsolatot!")
            return False
        except Exception as e:
            print(f"[✗] Authentikálási hiba: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def get_sites(self) -> Optional[list]:
        """
        Lekérdezi az összes site-ot a Catalyst Center-ből

        Returns:
            list: Site-ok listája vagy None ha hiba
        """
        try:
            print("\n[*] Site-ok lekérdezése...")

            url = f"{self.base_url}/sites"
            response = self.session.get(url, verify=self.verify_ssl, timeout=10)

            if response.status_code == 200:
                sites = response.json().get('response', [])
                print(f"[✓] {len(sites)} site találva")
                return sites
            else:
                print(f"[✗] Hiba a site-ok lekérdezésénél: HTTP {response.status_code}")
                return None

        except Exception as e:
            print(f"[✗] Hiba: {str(e)}")
            return None

    def find_site_by_hierarchy(self, sites: list, hierarchy_path: str) -> Optional[Dict[str, Any]]:
        """
        Megtalálja a site-ot a hierarchia alapján (pl. Global/Hungary/Budapest/Enterprise)

        Args:
            sites: Site-ok listája
            hierarchy_path: Hierarchia útvonal

        Returns:
            dict: A site adatai vagy None
        """
        try:
            print(f"\n[*] Site keresése: {hierarchy_path}")

            for site in sites:
                # A site hierarchia-ja az "siteNameHierarchy" mezőben van tárolva
                site_hierarchy = site.get('siteNameHierarchy', '')

                if site_hierarchy == hierarchy_path:
                    print(f"[✓] Site megtalálva!")
                    print(f"    Site ID: {site.get('id')}")
                    print(f"    Hierarchia: {site_hierarchy}")
                    return site

            print(f"[✗] Site nem található: {hierarchy_path}")
            print("\n[*] Elérhető site-ok:")
            for site in sites:
                print(f"    - {site.get('siteNameHierarchy')}")

            return None

        except Exception as e:
            print(f"[✗] Hiba a site keresésénél: {str(e)}")
            return None

    def reserve_ip_pool(self, site_id: str, ip_pool_name: str, cidr: str, gateway: str, vlan: int = 1304) -> bool:
        """
        Reserválja az IP poolt a site-hoz

        Args:
            site_id: Site ID
            ip_pool_name: IP pool neve
            cidr: IP cím tartomány (pl. 10.110.4.0/24)
            gateway: Default gateway IP cím
            vlan: VLAN ID

        Returns:
            bool: True ha sikeres, False ha hiba
        """
        try:
            print(f"\n[*] IP pool reserválása...")
            print(f"    Pool név: {ip_pool_name}")
            print(f"    CIDR: {cidr}")
            print(f"    Gateway: {gateway}")
            print(f"    VLAN: {vlan}")

            # IP cím és subnet mask kinyerése a CIDR notációból
            ip_and_mask = cidr.split('/')
            ip_address = ip_and_mask[0]
            prefix_length = int(ip_and_mask[1])

            # Subnet mask kiszámítása
            subnet_mask = self._calculate_subnet_mask(prefix_length)

            # IP pool request payload
            payload = {
                "siteId": site_id,
                "ipPoolName": ip_pool_name,
                "type": "LAN",
                "ipv4AddressSpace": [
                    {
                        "ipv4Cidr": cidr,
                        "ipv4Gateway": gateway,
                        "ipv4Prefix": True,
                        "ipv4DhcpServers": [],
                        "ipv4DnsServers": [],
                        "dhcpServerAddress": []
                    }
                ],
                "ipv6AddressSpace": [],
                "commonSettings": {
                    "inheritedPoolName": "",
                    "dhcpEnabled": True,
                    "dnsEnabled": False
                },
                "advancedSettings": {
                    "dhcpOption": [
                        {
                            "optionCode": 24,
                            "optionDescription": "VLAN ID",
                            "optionValue": str(vlan),
                            "optionGroup": "POLICY"
                        }
                    ]
                }
            }

            # API hívás IP pool reserválásához
            url = f"{self.base_url}/reserve-ip-subnet"

            print("\n[*] API hívás:")
            print(f"    URL: {url}")
            print(f"    Method: POST")

            response = self.session.post(
                url,
                json=payload,
                verify=self.verify_ssl,
                timeout=15
            )

            if response.status_code in [200, 201, 202]:
                print(f"\n[✓] IP pool sikeresen reserválva!")
                print(f"    HTTP Status: {response.status_code}")

                # Válasz feldolgozása
                if response.text:
                    try:
                        response_data = response.json()
                        print(f"    Válasz: {json.dumps(response_data, indent=2)}")
                    except:
                        pass

                return True
            else:
                print(f"\n[✗] Hiba az IP pool reserválásánál: HTTP {response.status_code}")
                print(f"    Válasz: {response.text}")
                return False

        except Exception as e:
            print(f"[✗] Hiba: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    @staticmethod
    def _calculate_subnet_mask(prefix_length: int) -> str:
        """
        CIDR prefix hosszból subnet mask-ot számít ki

        Args:
            prefix_length: CIDR prefix hossz (0-32)

        Returns:
            str: Subnet mask (pl. 255.255.255.0)
        """
        mask = (0xffffffff >> (32 - prefix_length)) << (32 - prefix_length)
        return '.'.join([str((mask >> (i << 3)) & 0xff) for i in range(3, -1, -1)])

    def close(self):
        """
        Session bezárása
        """
        if self.session:
            self.session.close()
            print("[✓] Session bezárva")


def main():
    """
    Főprogram
    """
    print("=" * 70)
    print("Cisco Catalyst Center IP Pool Reservation Script")
    print("=" * 70)

    # Konfigurációs paraméterek
    catalyst_center_ip = "10.8.11.100"
    username = "admin"
    ip_pool_name = "FABRIC1-Enterprise-TV-10.110.4.0/24-Vlan1304"
    ip_pool_cidr = "10.110.4.0/24"
    default_gateway = "10.110.4.1"
    site_hierarchy = "Global/Hungary/Budapest/Enterprise"  # ✓ HELYES SITE
    site_id = "1e10fadb-f994-4501-bacb-0dfe5be0bd9a"  # ✓ SITE ID
    vlan_id = 1304

    # Jelszó bekérése
    print(f"\nFelhasználónév: {username}")
    password = getpass.getpass("Jelszó: ")

    if not password:
        print("[✗] Hiba: Jelszó nem adható meg üres értékkel!")
        sys.exit(1)

    # Catalyst Center API kliens inicializálása
    cc_api = CatalystCenterAPI(
        host=catalyst_center_ip,
        username=username,
        password=password,
        verify_ssl=False
    )

    try:
        # 1. Authentikáció
        if not cc_api.authenticate():
            print("\n[✗] Authentikáció sikertelen!")
            sys.exit(1)

        # 2. Site információ
        print(f"\n[*] Site információ:")
        print(f"    Hierarchia: {site_hierarchy}")
        print(f"    Site ID: {site_id}")

        # Opcionális: Ellenőrzés - site-ok lekérdezése és validálása
        print(f"\n[*] Site-ok lekérdezése (ellenőrzés céljából)...")
        sites = cc_api.get_sites()
        if sites:
            print(f"[✓] {len(sites)} site elérhető")
            # Keressük meg ezt az ID-t a listában
            found = False
            for site in sites:
                if site.get('id') == site_id:
                    print(f"[✓] Site ID validálva: {site.get('siteNameHierarchy')}")
                    found = True
                    break
            if not found:
                print(f"[!] Figyelmeztetés: Site ID nem található a listában")
                print(f"    De folytatjuk a reserválást (ID: {site_id})")
        else:
            print(f"[!] Nem sikerült lekérdezni a site-okat, de folytatjuk a reserválást")

        # 4. IP pool reserválása
        success = cc_api.reserve_ip_pool(
            site_id=site_id,
            ip_pool_name=ip_pool_name,
            cidr=ip_pool_cidr,
            gateway=default_gateway,
            vlan=vlan_id
        )

        if success:
            print("\n" + "=" * 70)
            print("SIKERES BEFEJEZÉS!")
            print("=" * 70)
            print(f"\n[✓] IP Pool adatai:")
            print(f"    Név: {ip_pool_name}")
            print(f"    CIDR: {ip_pool_cidr}")
            print(f"    Gateway: {default_gateway}")
            print(f"    VLAN: {vlan_id}")
            print(f"    Site: {site_hierarchy}")
            print(f"    Site ID: {site_id}")
        else:
            print("\n" + "=" * 70)
            print("HIBA A RESERVÁLÁS SORÁN!")
            print("=" * 70)
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n[!] Felhasználó által abbahagyva")
        sys.exit(0)
    except Exception as e:
        print(f"\n[✗] Váratlan hiba: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        cc_api.close()


if __name__ == "__main__":
    main()
