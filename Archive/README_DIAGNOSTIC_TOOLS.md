# 🔧 Catalyst Center Diagnosztikai Eszközök

## 📋 Overview

A 401 Unauthorized hiba megoldásához 3 új eszköz lett kiadva:

1. **`catalyst_center_diagnostic.py`** - Automatikus diagnosztika
2. **`SOLVE_401_QUICKLY.md`** - Gyors 5 perces megoldás
3. **`TROUBLESHOOTING_401.md`** - Részletes hibaelhárítás

---

## 🎯 MELYIKET HASZNÁLJAM?

### Szituáció 1: "HTTP 401 kapok, nincs ötletem"
→ **FUTTASD:** `python catalyst_center_diagnostic.py`

```bash
python catalyst_center_diagnostic.py
```

Ez automatikusan:
- Tesztel az API-val
- Próbál több authentikációs módot
- Javaslatokat ad

---

### Szituáció 2: "5 percen belül megoldani szeretném"
→ **OLVASD:** `SOLVE_401_QUICKLY.md`

Ez egy döntési fa (decision tree) amit követve 5 perc alatt megoldható a probléma.

---

### Szituáció 3: "Mélyebben szeretném megérteni a problémát"
→ **OLVASD:** `TROUBLESHOOTING_401.md`

Ez egy komprehenzív útmutató, amely:
- 6 lehetséges ok-ot ismertet
- Lépésenkénti megoldást ad
- Ellenőrzési listákat tartalmaz

---

## 🚀 QUICK START

### 1. DIAGNOSTIC FUTTATÁSA

```bash
# Windows
python catalyst_center_diagnostic.py

# Linux/Mac
python3 catalyst_center_diagnostic.py
```

### 2. OUTPUT OLVASÁSA

A script kiírja, hogy:
- ✓ Sikeres a hálózati kapcsolat?
- ✓ Sikeres az authentikáció?
- ✓ Melyik API verzió működik?
- ! Milyen javaslatokat ad?

### 3. JAVASLATOKAT KÖVESD

A diagnostic script végén javaslatokat kap azzal, hogy:
- Melyik API verzió szükséges
- Milyen authentikációs mód működik
- Mit próbálj meg következőnek

---

## 📊 DIAGNOSTIC SCRIPT LÉPÉSEIRŐL LÉPÉSRE

A script 5 fő tesztet futtat:

### 1. HÁLÓZATI KAPCSOLAT TESZTELÉSE
```
[*] 1. HÁLÓZATI KAPCSOLAT TESZTELÉSE
```
- Ellenőrzi, hogy elérhető-e a 10.8.11.100
- Ha nem: hálózati probléma van

### 2. BASIC AUTH TESZTELÉSE
```
[*] 2. BASIC AUTH TESZTELÉSE
```
- Próbálja az API v1 és v2 Basic Auth-ot
- Ha sikeres: az alapvető auth működik

### 3. HEADER AUTH TESZTELÉSE
```
[*] 3. HEADER-ALAPÚ AUTH TESZTELÉSE
```
- Próbálja az alternatív authentikációs módot
- Néhány CC verzió ezt előnyben részesíti

### 4. CC VERZIÓ LEKÉRDEZÉSE
```
[*] 4. CATALYST CENTER VERZIÓ LEKÉRDEZÉSE
```
- Megjeleníti a CC verzióját
- Fontos az API kompatibilitáshoz

### 5. SITE LEKÉRDEZÉSE (Token szükséges)
```
[*] 5. SITE-OK LEKÉRDEZÉSÉNEK TESZTELÉSE
```
- Ha van token, listázza az elérhető site-okat
- Ellenőrzi, hogy az "Enterprise" site elérhető-e

---

## 🎯 LEHETSÉGES KIMENETELEI A DIAGNOSTIC-NAK

### KIMENETEL 1: SIKER ✓

```
[✓] CC elérhető: 10.8.11.100
[✓] Basic Auth sikeres (v1)!
[✓] Verzió lekérdezve
[✓] Authentikáció sikeres!
```

**Megoldás:** Futtathatod az eredeti scriptet

```bash
python catalyst_center_ip_pool_reservation.py
```

---

### KIMENETEL 2: HÁLÓZATI HIBA ✗

```
[✗] Nem lehet csatlakozni: 10.8.11.100
```

**Megoldás:**
```bash
# Ellenőrizd a hálózati kapcsolatot
ping 10.8.11.100

# Ha nem működik:
# 1. Ellenőrizd az IP cím helyességét
# 2. Firewall/proxy blokkolja?
# 3. Tunnel vagy VPN szükséges?
```

---

### KIMENETEL 3: AUTHENTIKÁLÁSI HIBA ✗

```
[!] Test 1: /dna/intent/api/v1/auth/token
    HTTP Status: 401
```

**Megoldás:** Olvasd el a `TROUBLESHOOTING_401.md` файlt vagy a `SOLVE_401_QUICKLY.md`-t

---

### KIMENETEL 4: API VERZIÓ ELTÉRÉS ✗

```
[!] Test 1: v1 - HTTP 401
[✓] Test 2: v2 - HTTP 200
```

**Megoldás:** A script automatikusan v2-t fog használni a következő futtatásnál

---

## 💡 DIAGNOSTIC SCRIPT KIMENETEIBŐL HOGYAN OLVASSAM EL A PROBLÉMÁKAT?

### Keress ezekre az jelekre:

| Jel | Jelentése | Mit tegyél |
|-----|-----------|-----------|
| `[✓]` | Sikeres teszt | Nincs teendő, továbblépés |
| `[!]` | Figyelmeztetés, próbálja a következő módot | Fortsetzung |
| `[✗]` | Kritikus hiba, megáll a teszt | Olvasd el a javaslatokat |

### Például:
```
[✓] CC elérhető - OK
[!] v1 API nem működik - próbálkozunk v2-vel
[✓] v2 API működik - siker!
```

---

## 🔧 A JAVÍTOTT EREDETI SCRIPT (catalyst_center_ip_pool_reservation.py)

Az eredeti script is frissült:

**Új funkciók:**
- ✅ Automatikusan próbálja v1 és v2 API-t
- ✅ JSON Body Auth támogatás
- ✅ Jobb error üzenetek
- ✅ Javaslatokat ad 401-es hiba esetén
- ✅ Linkelést mutat a diagnostic scriptre

**Futtatás:**
```bash
python catalyst_center_ip_pool_reservation.py
```

---

## 📋 FÁJLOK GYORS REFERENCIA

| Fájl | Méret | Funkció | Mikor |
|------|-------|---------|-------|
| `catalyst_center_diagnostic.py` | 8 KB | 🔧 Automatikus diagnosztika | Első 401-es hiba |
| `SOLVE_401_QUICKLY.md` | 4 KB | ⚡ Gyors 5 perces megoldás | Gyorsmegoldás szükséges |
| `TROUBLESHOOTING_401.md` | 12 KB | 📖 Részletes útmutató | Mélyebb megértéshez |
| `catalyst_center_ip_pool_reservation.py` | 12 KB | 📝 Eredeti frissített script | IP pool reserválás |

---

## 🎓 TANULÁSI ÚTVONAL

### Kezdő szint (5 perc)
1. `SOLVE_401_QUICKLY.md` → Gyors diagnózis
2. `python catalyst_center_diagnostic.py` → Automatikus teszt

### Közép szint (15 perc)
1. `TROUBLESHOOTING_401.md` → OK kódok megértése
2. `catalyst_center_diagnostic.py` → Részletes output elemzés
3. CC Admin felület → User & Roles ellenőrzés

### Haladó szint (30+ perc)
1. Catalyst Center dokumentáció
2. API v1 vs v2 különbségek
3. LDAP/AD integráció
4. Custom API paraméterek

---

## ✅ TROUBLESHOOTING CHECKLIST

```
☐ Diagnostic script letöltve
☐ Diagnostic script futtatva: python catalyst_center_diagnostic.py
☐ Output átnézve
☐ Javaslatokat követtem
☐ Admin web felületre bejelentkeztem
☐ LDAP/LOCAL felhasználó típusa ellenőrizve
☐ Jelszó helyességét tesztelem
☐ Speciális karakterek escaped-ek
☐ Új admin felhasználó létrehozva (ha szükséges)
☐ Diagnostic újra futtatva
☐ Eredeti script futtatva
☐ IP pool sikeresen reserválva
```

---

## 🚀 KÖVETKEZŐ LÉPÉSEK SIKER UTÁN

Ha a diagnostic sikeres:

```bash
1. Futtasd az eredeti IP pool scriptet:
   python catalyst_center_ip_pool_reservation.py

2. Add meg az admin jelszavát

3. A script automatikusan:
   - Megtalálja a Global/Hungary/Budapest/Enterprise site-ot
   - Reserválja a 10.110.4.0/24 IP pool-t
   - Beállítja a 10.110.4.1 gateway-t
   - Hozzáadja az 1304-es VLAN-t
```

---

## 📞 TÁMOGATÁS

**Probléma?**

1. Futtasd a diagnostic scriptet
2. Olvasd el a javaslatokat
3. Olvasd el a `TROUBLESHOOTING_401.md` dokumentációt
4. Ha még mindig nem működik, kontaktálj Cisco support-ot (diagnostic output mellékelve)

---

**Good luck! 🚀**
