# 🔧 Hibaelhárítás: HTTP 401 Unauthorized - Catalyst Center

## ⚠️ A Hiba

```
[✗] Authentikálási hiba: HTTP 401
    Válasz: {"message":"Unauthorized"}
```

Ez azt jelenti, hogy az authentikáció sikertelen. Az alábbi lépéseket kövesd a megoldáshoz.

---

## 🔍 DIAGNOSZTIKA - 1. LÉPÉS

Először futtasd a **diagnostikai scriptet**, amely teszteli az authentikációs módokat:

```bash
python catalyst_center_diagnostic.py
```

Ez a script:
- ✅ Tesztel a hálózati kapcsolatot
- ✅ Próbálja a Basic Auth-ot (v1 és v2 API-val)
- ✅ Próbálja a Header Auth-ot
- ✅ Lekérdezi a CC verzióját
- ✅ Javaslatokat ad

---

## 🚨 LEHETSÉGES OKOK

### OK #1: Helytelen Jelszó (LEGVALÓSZÍNŰBB)

**Tünetek:**
- Az admin jelszó változott meg
- Félrenyomtad a jelszót

**Megoldás:**
```bash
1. Próbálkozz meg manuálisan bejelentkezni:
   https://10.8.11.100
   
2. Ha az web felületre is 401-et kapsz → biztosan rossz a jelszó

3. Ha működik az web felületen → az API más hitelesítést használ
```

### OK #2: LDAP/Active Directory Authentikáció

**Tünetek:**
- A CC LDAP/AD-vel van konfigurálva
- Az admin felhasználó LDAP-os felhasználó
- Az API-k másképp kezelik az auth-ot

**Megoldás:**
```bash
1. Menj az CC admin felületére:
   https://10.8.11.100
   
2. System → Administration → User & Roles
   
3. Ellenőrizd az admin felhasználó típusát:
   - LOCAL USER → az API-nak működnie kell
   - LDAP/AD USER → az API másképp működhet
   
4. Ha LDAP: próbálkozz az LDAP felhasználóneveddel:
   - username@domain.com
   - DOMAIN\username
```

### OK #3: API Verzió Eltérés

**Tünetek:**
- CC 2.3 vagy újabb verzió
- Az API endpoint másképp működik
- Basic Auth nem működik

**Megoldás:**
```bash
1. Ellenőrizd a CC verzióját:
   - Web felületet: https://10.8.11.100
   - Jobb felső sarok: "About" vagy verzió info
   
2. Ha CC 2.3+:
   - Az API v1 helyett v2-t kell használni
   - Az authentikáció módja módosult
   
3. Javasolt: Futtasd a diagnostic scriptet
   - Az automatikusan teszteli v1 és v2 API-kat
```

### OK #4: API Hozzáférés Korlátozva

**Tünetek:**
- Az admin felhasználó nem rendelkezik API hozzáféréssel
- Az admin role nem engedélyez API-t

**Megoldás:**
```bash
1. Menj az CC admin felületére:
   https://10.8.11.100
   
2. System → Administration → User & Roles
   
3. Ellenőrizd az admin felhasználó role-jait:
   - ADMIN role-nak kell lennie
   - API hozzáférésnek engedélyezve kell lennie
   
4. Ha korlátozva van: módosítsd az admin felhasználót
   vagy hozz létre egy új admin felhasználót
```

### OK #5: Speciális Karakterek a Jelszóban

**Tünetek:**
- A jelszó tartalmaz @ ! $ % # & ( ) stb. karaktereket
- Az escape-elés hiányzik

**Megoldás:**
```bash
# Az alábbi karaktereket escape-elni kell:
- @ → \@
- ! → \!
- $ → \$
- % → \%
- # → \#
- & → \&
- ( ) → \( \)

# Alternatíva: Használj egy egyszerűbb jelszót (alphanumerikus)
```

### OK #6: Catalyst Center Verziójának Problémai

**Tünetek:**
- Az authentikáció konzisztensen 401-et ad
- Az alkalmazás crash-et generál

**Megoldás:**
```bash
1. Ellenőrizd a CC naplóit:
   System → Logs
   
2. Keress "authentication" vagy "API" hibákat
   
3. Indítsd újra a CC-t:
   System → Services → Restart
   
4. Próbáld a diagnostic scriptet
```

---

## ✅ LÉPÉSEK A PROBLÉMA MEGOLDÁSÁHOZ

### **LÉPÉS 1: Diagnostic Script Futtatása**

```bash
python catalyst_center_diagnostic.py
```

**Figyeld meg az outputot:**
- Melyik test passou meg?
- Melyik test buklott meg?
- Milyen hibakódok jöttek?

### **LÉPÉS 2: Ellenőrzés az Admin Felületen**

```
1. Nyiss egy böngészőt
2. Menj ide: https://10.8.11.100
3. Login az admin felhasználóval
4. Ha bejelenkezés sikeres → az API másképp működik
5. Ha bejelentkezés sikertelen → valóban rossz a jelszó
```

### **LÉPÉS 3: CC Verzió Ellenőrzése**

```
1. https://10.8.11.100 → jobb felső sarok
2. Keress "About" vagy verzió információt
3. Jegyezd fel a verzió számot
4. Ellenőrizd az alábbi támogatott verziók közül:
   - CC 2.2 → API v1
   - CC 2.3 → API v1 és v2
   - CC 2.4 → API v2 ajánlott
```

### **LÉPÉS 4: Felhasználó Role Ellenőrzése**

```
1. Admin felület → System → User & Roles
2. Kattints az admin felhasználóra
3. Ellenőrizd:
   - ADMIN role-e van?
   - API hozzáférés engedélyezve?
   - LDAP vagy LOCAL user?
```

### **LÉPÉS 5: Új Admin Felhasználó Létrehozása (Ha Szükséges)**

```bash
Ha az admin felhasználó problémás:

1. Admin felület → System → User & Roles
2. Új felhasználó: "ccadmin"
3. Jelszó: egyszerű, alphanumerikus (pl. "Cisco123")
4. Role: ADMIN
5. Próbáld az eredeti scriptet az új felhasználóval
```

### **LÉPÉS 6: Script Módosítása az API Verzióhoz**

Ha a diagnostic script azt mutatja, hogy v2 API szükséges, módosítsd az eredeti scriptet:

```python
# A catalyst_center_ip_pool_reservation.py-ben:

# Módosítsd ezt:
self.base_url = f"https://{host}/dna/intent/api/v1"

# Erre (v2):
self.base_url = f"https://{host}/dna/intent/api/v2"
```

---

## 📋 ELLENŐRZÉSI LISTA

```
☐ Diagnostic script futtatva
☐ Admin jelszó helyesen gépelt
☐ CC verzió ellenőrzve
☐ Admin user role ellenőrzve
☐ API hozzáférés engedélyezve
☐ LDAP/AD authentikáció ellenőrzve
☐ Speciális karakterek escaped-ek
☐ Hálózati kapcsolat OK
☐ Firewall/Proxy nincs blokkolva
```

---

## 🆘 HA MÉG MINDIG NEM MŰKÖDIK

### Gyűjtsd össze az alábbi információkat:

1. **Diagnostic script outputja** - Másold be az összes kimenetet
2. **CC verzió** - Pontosan mely verzió?
3. **Admin felhasználó típusa** - LOCAL vagy LDAP?
4. **CC naplók** - Milyen error-ok vannak a naplóban?
5. **Jelszó** - Tartalmaz-e speciális karaktereket?

### Bejelentési sablonon:

```
Hiba: HTTP 401 Unauthorized
Catalyst Center IP: 10.8.11.100
CC verzió: [verzió]
Admin user típusa: [LOCAL/LDAP]
Diagnostic output: [output]
CC naplók: [error messages]
```

---

## 🔗 TOVÁBBI SEGÍTSÉGEK

### Cisco Dokumentáció:
- [Catalyst Center 2.3 Admin Guide](https://www.cisco.com/c/en/us/support/docs/)
- [DNA Center API Documentation](https://developer.cisco.com/docs/dna-center/)

### Common Solutions:
1. **Password reset:** https://10.8.11.100 → Forgot Password?
2. **User & Role Management:** https://10.8.11.100 → System → User & Roles
3. **API Permissions:** https://10.8.11.100 → System → Settings → API

---

## 💡 GYORS TIPPEK

| Hiba | Megoldás |
|------|----------|
| 401 + LDAP | Próbáld: `admin@domain.com` vagy `DOMAIN\admin` |
| 401 + Speciális karakter | Escape: `@` → `\@`, `!` → `\!` |
| 401 + CC 2.3+ | Próbáld az API v2-t |
| 401 + Web login OK | Az API más route-ot használ |
| 401 + Web login sikertelen | Valóban rossz a jelszó |

---

## ✨ SIKERES AUTHENTIKÁCIÓ JELEI

Ha a diagnostic script azt mutatja:

```
[✓] CC elérhető: 10.8.11.100
[✓] Basic Auth sikeres (v1)!
[✓] Verzió lekérdezve
[✓] Authentikáció sikeres!
```

**Gratulálunk!** Mostmár futtathatod az eredeti scriptet:

```bash
python catalyst_center_ip_pool_reservation.py
```

---

**Ha még kérdésed van, futtasd a diagnostic scriptet és küldj nekünk az outputot!** 🚀
