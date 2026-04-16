"""
Catalyst Center IP Pool Reservation - Konfigurációs fájl sablon

HASZNÁLAT:
---------
1. Másold ezt a fájlt: config_example.py -> config.py
2. Módosítsd az alábbi paramétereket az igényeidnek megfelelően
3. Futtasd a scriptet: python catalyst_center_ip_pool_reservation.py
"""

# ============================================================================
# CATALYST CENTER KONFIGURÁLÁSA
# ============================================================================

# Catalyst Center IP cím vagy hostname
CATALYST_CENTER_HOST = "10.8.11.100"

# Felhasználónév (jelszót a script bekéri)
USERNAME = "admin"

# SSL tanúsítvány ellenőrzése (éles envben: True)
VERIFY_SSL = False

# ============================================================================
# IP POOL KONFIGURÁLÁSA
# ============================================================================

# IP pool neve (egyedi kell, hogy legyen a CC-ben)
IP_POOL_NAME = "FABRIC1-Enterprise-TV-10.110.4.0/24-Vlan1304"

# IP cím tartomány CIDR formátumban (pl. 10.110.4.0/24)
IP_POOL_CIDR = "10.110.4.0/24"

# Default gateway IP cím
DEFAULT_GATEWAY = "10.110.4.1"

# VLAN ID (opcionális, de ajánlott)
VLAN_ID = 1304

# ============================================================================
# SITE KONFIGURÁLÁSA
# ============================================================================

# Site hierarchia útvonal (pl. Global/Hungary/Budapest/Enterprise)
# A script megjeleníti az összes elérhető site-ot, ha ez nem található
SITE_HIERARCHY = "Global/Hungary/Budapest/Enterprise"

# ============================================================================
# EGYÉB BEÁLLÍTÁSOK
# ============================================================================

# API timeout (másodperc)
API_TIMEOUT = 15

# Detailliert kimeneti szint (True = verbose, False = minimal)
VERBOSE_OUTPUT = True

# ============================================================================
# DHCP BEÁLLÍTÁSOK
# ============================================================================

# DHCP engedélyezve az IP pool-hoz?
DHCP_ENABLED = True

# DHCP szerverek (üres = nem specifikus)
DHCP_SERVERS = []

# DNS szerverek (üres = CC alapértelmezettje)
DNS_SERVERS = []

# ============================================================================
# PÉLDÁK KÜLÖNBÖZŐ KONFIGURÁCIÓKHOZ
# ============================================================================

"""
EXAMPLE 1 - Szeged Site, Guest Network:
------
IP_POOL_NAME = "FABRIC1-Guest-TV-10.120.4.0/24-Vlan1305"
IP_POOL_CIDR = "10.120.4.0/24"
DEFAULT_GATEWAY = "10.120.4.1"
VLAN_ID = 1305
SITE_HIERARCHY = "Global/Hungary/Szeged"

EXAMPLE 2 - Budapest Site, IoT Network:
------
IP_POOL_NAME = "FABRIC1-IoT-TV-10.130.4.0/24-Vlan1306"
IP_POOL_CIDR = "10.130.4.0/24"
DEFAULT_GATEWAY = "10.130.4.1"
VLAN_ID = 1306
SITE_HIERARCHY = "Global/Hungary/Budapest/IoT"

EXAMPLE 3 - Debrecen Site, Management Network:
------
IP_POOL_NAME = "FABRIC1-Mgmt-TV-10.140.4.0/24-Vlan1307"
IP_POOL_CIDR = "10.140.4.0/24"
DEFAULT_GATEWAY = "10.140.4.1"
VLAN_ID = 1307
SITE_HIERARCHY = "Global/Hungary/Debrecen"
"""
