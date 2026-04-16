# ⚡ Gyors Kezdőkalauz - Catalyst Center IP Pool Reservation Script

## 📦 Telepítés (2 perc)

### 1. Szükséges Könyvtárak Telepítése

```bash
pip install -r requirements.txt
```

Vagy közvetlenül:
```bash
pip install requests urllib3
```

### 2. Script Futtatása

```bash
python catalyst_center_ip_pool_reservation.py
```

---

## 🎯 Alapvető Munkafolyamat

```
1. Script indítása
   ↓
2. Jelszó bekérése (admin felhasználó jelszava)
   ↓
3. Catalyst Center authentikálása
   ↓
4. Site-ok lekérdezése
   ↓
5. Szükséges site megtalálása (Global/Hungary/Budapest/Enterprise)
   ↓
6. IP pool reserválása
   ↓
7. Megerősítés a sikeres lezárásról
```

---

## ✅ Előfeltételek

- ✅ Python 3.6 vagy újabb
- ✅ Admin hozzáférés a Catalyst Center-hez
- ✅ Hálózati kapcsolat a CC-hez (10.8.11.100 elérhető)
- ✅ Az admin jelszó ismerete

---

## 🚀 Példa Futtatás

```bash
$ python catalyst_center_ip_pool_reservation.py

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
    Site ID: abc123def456

[*] IP pool reserválása...
[✓] IP pool sikeresen reserválva!

======================================================================
SIKERES BEFEJEZÉS!
======================================================================
```

---

## 🔧 Konfigurálás Más IP Pool-hez

### Módszer 1: Python Script Szerkesztése

Szerkeszd a script elejét (`main()` függvényt):

```python
# A main() függvényen belül:
ip_pool_name = "FABRIC1-Guest-TV-10.120.4.0/24-Vlan1305"
ip_pool_cidr = "10.120.4.0/24"
default_gateway = "10.120.4.1"
site_hierarchy = "Global/Hungary/Szeged"
vlan_id = 1305
```

### Módszer 2: Config Fájl Használata (Advanced)

1. Másold a `config_example.py`-t: `config.py`-ba
2. Szerkeszd a paramétereket `config.py`-ban
3. Importáld a config-ot a scriptbe

---

## ❌ Hibakezelés

### "Site nem található"

Ha ezt az üzenetet látod:
```
[✗] Site nem található: Global/Hungary/Budapest/Enterprise

[*] Elérhető site-ok:
    - Global
    - Global/Hungary
    - Global/Hungary/Budapest
```

**Megoldás:** 
- Ellenőrizd az elérhető site-ok közül a helyes hierarchia útvonalat
- Módosítsd a `site_hierarchy` értéket a scriptben

### "Authentikálási hiba"

```
[✗] Authentikálási hiba: HTTP 401
```

**Megoldás:**
- Ellenőrizd az admin jelszót
- Biztos, hogy az admin felhasználó aktív?

### "Nem elérhető"

```
[✗] Kapcsolódási hiba: 10.8.11.100 nem elérhető
```

**Megoldás:**
- Ping tesztel: `ping 10.8.11.100`
- Ellenőrizd a hálózati kapcsolatot
- Valóban ez-e a CC IP cím?

---

## 📊 Mit Csináls a Script?

A script az alábbi adatokat reserválja:

| Paraméter | Érték |
|-----------|-------|
| **Pool Név** | `FABRIC1-Enterprise-TV-10.110.4.0/24-Vlan1304` |
| **IP Tartomány** | `10.110.4.0/24` (64 IP cím) |
| **Gateway** | `10.110.4.1` |
| **VLAN** | `1304` |
| **Site** | `Global/Hungary/Budapest/Enterprise` |
| **DHCP** | Engedélyezve |

---

## 🔐 Biztonsági Tipek

1. ✅ Ne mentsd el a jelszót fájlokba
2. ✅ Használj erős jelszavakat
3. ✅ Ellenőrizd az SSL tanúsítványt éles szinten
4. ✅ Korlátoz az admin hozzáférést

---

## 📚 További Információk

- 📖 Teljes dokumentáció: `README_catalyst_center_ip_pool.md`
- 🔧 Konfigurációs sablonok: `config_example.py`
- 📋 API referencia: Cisco Developer Documentation

---

## 💡 Tippek

**Tipp 1:** Ha sok IP pool-t szeretnél reserválni, módosítsd a scriptet loop-al vagy batch módban.

**Tipp 2:** Teszteld először egy dev CC-n, mielőtt éles-ben futtatnál.

**Tipp 3:** Mentsd meg az output-ot auditáláshoz:
```bash
python catalyst_center_ip_pool_reservation.py > reservation_log.txt 2>&1
```

---

**Sok sikert a Catalyst Center kezeléséhez! 🎉**
