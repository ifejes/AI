# Cisco Catalyst Center IP Pool Reservation Script

## 📋 Leírás

Python script, amely csatlakozik a Cisco Catalyst Center REST API-hoz és reservál egy IP poolt (10.110.4.0/24) az **Global/Hungary/Budapest/Enterprise** site alá.

### Funkciók:
- ✅ Secure authentikáció (jelszó bekérésével)
- ✅ Site hierarchia alapú keresés
- ✅ IP pool reserválása a specifikus site-hoz
- ✅ VLAN beállítás (1304)
- ✅ Error handling és részletes output
- ✅ SSL tanúsítvány ellenőrzés kikapcsolt (self-signed tanúsítványhoz)

---

## 🔧 Telepítés

### Előfeltételek:
- **Python 3.6+**
- **pip** (Python package manager)

### Szükséges könyvtárak telepítése:

```bash
pip install requests
```

Vagy a `requirements.txt`-ből:

```bash
pip install -r requirements.txt
```

(Ha szükséges, fájl tartalmát alul találod)

---

## 🚀 Használat

### Basic futtatás:

```bash
python catalyst_center_ip_pool_reservation.py
```

### Futtatás lépések:

1. **Script indítása** - Python-nal futtatod
2. **Jelszó bekérése** - Meg kell adnod az `admin` felhasználó jelszavát
3. **Authentikáció** - Script csatlakozik a CC-hez
4. **Site keresés** - Megtalálja a Global/Hungary/Budapest/Enterprise site-ot
5. **IP Pool reserválása** - Létrehozza az IP poolt az alábbi paraméterekkel:
   - **Név:** `FABRIC1-Enterprise-TV-10.110.4.0/24-Vlan1304`
   - **IP tartomány:** `10.110.4.0/24`
   - **Default Gateway:** `10.110.4.1`
   - **VLAN:** `1304`

### Kimenet példa:

```
======================================================================
Cisco Catalyst Center IP Pool Reservation Script
======================================================================

Felhasználónév: admin
Jelszó: ••••••••••

[*] Csatlakozás a Catalyst Center-hez...
[✓] Sikeres authentikáció!

[*] Site-ok lekérdezése...
[✓] 5 site találva

[*] Site keresése: Global/Hungary/Budapest/Enterprise
[✓] Site megtalálva!
    Site ID: 1234567890abcdef
    Hierarchia: Global/Hungary/Budapest/Enterprise

[*] IP pool reserválása...
    Pool név: FABRIC1-Enterprise-TV-10.110.4.0/24-Vlan1304
    CIDR: 10.110.4.0/24
    Gateway: 10.110.4.1
    VLAN: 1304

[*] API hívás:
    URL: https://10.8.11.100/dna/intent/api/v1/reserve-ip-subnet
    Method: POST

[✓] IP pool sikeresen reserválva!
    HTTP Status: 200

======================================================================
SIKERES BEFEJEZÉS!
======================================================================

[✓] IP Pool adatai:
    Név: FABRIC1-Enterprise-TV-10.110.4.0/24-Vlan1304
    CIDR: 10.110.4.0/24
    Gateway: 10.110.4.1
    VLAN: 1304
    Site: Global/Hungary/Budapest/Enterprise
    Site ID: 1234567890abcdef

[✓] Session bezárva
```

---

## 🔐 Biztonsági Megjegyzések

### Jelszó Kezelése:
- A jelszó a `getpass` modullal kerül bekérésre (nem jelenik meg a képernyőn)
- A jelszó **nem** kerül naplózásra vagy fájlba mentésre
- A jelszó csak a session-ben tartózkodik memóriában

### SSL Tanúsítvány:
- Az SSL tanúsítvány ellenőrzése **kikapcsolt** (`verify_ssl=False`)
- Ez szükséges lehet, ha a Catalyst Center önálló aláírt tanúsítványt használ
- **Éles környezetben** javasolt az SSL ellenőrzés bekapcsolása és a tanúsítvány kezelése

---

## 📝 Konfigurálható Paraméterek

Ha más IP poolt szeretnél reserválni, módosítsd az alábbi sorokat a scripten belül (a `main()` függvényben):

```python
# Konfigurációs paraméterek
catalyst_center_ip = "10.8.11.100"      # CC IP cím
username = "admin"                       # Felhasználónév
ip_pool_name = "FABRIC1-Enterprise-TV-10.110.4.0/24-Vlan1304"  # Pool neve
ip_pool_cidr = "10.110.4.0/24"          # IP tartomány
default_gateway = "10.110.4.1"          # Default gateway
site_hierarchy = "Global/Hungary/Budapest/Enterprise"  # Site hierarchia
vlan_id = 1304                          # VLAN ID
```

### Más site-hoz reserváláshoz:

Például **Global/Hungary/Szeged** site-hoz:

```python
site_hierarchy = "Global/Hungary/Szeged"
```

A script megjeleníti az összes elérhető site-ot, ha a megadott nem található.

---

## 🐛 Hibakezelés

### Lehetséges hibák és megoldások:

| Hiba | Ok | Megoldás |
|------|----|----|
| `Kapcsolódási hiba: 10.8.11.100 nem elérhető` | CC nincs online vagy rossz IP | Ellenőrizd az IP cím és a hálózati kapcsolat |
| `Authentikálási hiba: HTTP 401` | Rossz jelszó | Ellenőrizd az admin jelszót |
| `Site nem található: Global/Hungary/Budapest/Enterprise` | Rossz hierarchia útvonal | Futtasd a scriptet, amely megjeleníti az elérhető site-okat |
| `Hiba az IP pool reserválásánál: HTTP 400` | Érvénytelen paraméterek | Ellenőrizd a CIDR formátumot és a gateway IP-t |
| `Timeout: A Catalyst Center nem válaszol` | Lassú hálózat vagy terhelés | Várd meg és próbálkozz újra |

---

## 📊 API Dokumentáció

### Használt API Endpoint-ok:

#### 1. Authentication (Authentikáció)
```
POST https://10.8.11.100/dna/intent/api/v1/auth/token
Headers:
  - Authorization: Basic <base64(admin:password)>
```

**Válasz:**
```json
{
  "Token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### 2. Get Sites (Site-ok lekérdezése)
```
GET https://10.8.11.100/dna/intent/api/v1/sites
Headers:
  - X-Auth-Token: <token>
```

**Válasz:**
```json
{
  "response": [
    {
      "id": "1234567890abcdef",
      "siteNameHierarchy": "Global/Hungary/Budapest/Enterprise",
      "siteNumber": 1,
      "name": "Enterprise"
    }
  ]
}
```

#### 3. Reserve IP Subnet (IP Pool reserválása)
```
POST https://10.8.11.100/dna/intent/api/v1/reserve-ip-subnet
Headers:
  - X-Auth-Token: <token>
  - Content-Type: application/json

Body:
{
  "siteId": "1234567890abcdef",
  "ipPoolName": "FABRIC1-Enterprise-TV-10.110.4.0/24-Vlan1304",
  "type": "LAN",
  "ipv4AddressSpace": [
    {
      "ipv4Cidr": "10.110.4.0/24",
      "ipv4Gateway": "10.110.4.1",
      "ipv4Prefix": true,
      "ipv4DhcpServers": [],
      "ipv4DnsServers": [],
      "dhcpServerAddress": []
    }
  ],
  "commonSettings": {
    "dhcpEnabled": true
  }
}
```

---

## 🎯 Támogatott Catalyst Center Verziók

- ✅ **Catalyst Center 2.2+**
- ✅ **DNA Center 2.3+**

**Megjegyzés:** Az API strukturája eltérhet a verziók között. Ha más verzióval dolgozol, ellenőrizd a Cisco Official API dokumentációját.

---

## 📌 Jellemzők és Korlátozások

### Jellemzők:
- ✅ Automatikus site hierarchia keresés
- ✅ Teljes error handling
- ✅ Részletes logging és output
- ✅ Secure jelszóbekérés

### Korlátozások:
- ⚠️ Csak egy IP pool-t reservál futtatásonként
- ⚠️ SSL tanúsítvány ellenőrzés ki van kapcsolva
- ⚠️ Nincs egyezményes kezelés a CC lezárásához

---

## 🔄 Kiterjesztési Lehetőségek

### Lehetséges fejlesztések:
1. **Batch reserválás** - Több IP pool egyszerre
2. **Konfig fájl** - Paraméterek kiolvasása `config.yaml`-ből
3. **Database naplózás** - Végrehajtott műveletek naplózása adatbázisba
4. **Slack integrációs** - Sikeres/sikertelen notifikáció Slack-re
5. **Web felület** - Flask/FastAPI alapú web UI

---

## 📚 Szükséges Könyvtárak (`requirements.txt`)

```
requests>=2.25.0
urllib3>=1.26.0
```

Telepítéshez:
```bash
pip install -r requirements.txt
```

---

## 📞 Hibajelentés és Támogatás

Ha hibát találsz vagy kérdésed van:

1. **Ellenőrizd a CC verziót** - `https://10.8.11.100/dna`
2. **Nézd meg a CC naplókat** - System > Administration > Logs
3. **Futtasd a scriptet verbose módban** - A kimeneten láthatod az API válaszokat
4. **Ellenőrizd az alábbi helyek között az összekapcsoálódást:**
   - CC és a script közötti hálózati kapcsolat
   - Felhasználói jogosultságok (admin jogok szükségesek)
   - Site hierarchia helyes-e

---

## 📄 Licenc és Szerzői Jog

**Szerző:** AI Assistant  
**Verzió:** 1.0  
**Utolsó módosítás:** 2026-04-16

Ez a script az oktatási és belső felhasználásra készült.

---

## 🎓 Cisco Catalyst Center API Hivatkozások

- [Cisco Catalyst Center API dokumentáció](https://developer.cisco.com/docs/dna-center/)
- [Catalyst Center 2.3 API referencia](https://developer.cisco.com/dna-center-api-docs/)
- [IP Address Pool Management](https://developer.cisco.com/docs/dna-center/#!reserve-ip-subnet)

---

**Jó sorút a Catalyst Center kezeléséhez! 🚀**
