# ⚡ Gyors 401-es Hiba Megoldása - 5 Perc

## 🚀 AZONNALI MEGOLDÁS

### 1. DIAGNOSTIC SCRIPT FUTTATÁSA (1 perc)

```bash
python catalyst_center_diagnostic.py
```

**Ez automatikusan tesztel:**
- ✅ Hálózati kapcsolat
- ✅ Basic Auth (API v1 és v2)
- ✅ JSON Body Auth
- ✅ CC verzió
- ✅ Site-ok hozzáférés

**Output után javaslatokat adol kapni!**

---

### 2. ELLENŐRIZD AZ OUTPUTOT

**Ha látsz ilyet:**
```
[✓] Basic Auth sikeres (v1)!
```
→ **KÉSZ!** Futtathatod az eredeti scriptet

**Ha nem működik:**
→ Ugrass a 3. lépésre

---

### 3. ELLENŐRZÉS AZ ADMIN FELÜLETEN (2 perc)

```
1. Nyiss böngészőt
2. https://10.8.11.100
3. Login admin / jelszó
```

**Sikeres login?**
- **IGEN** → Az API másképp működik, lásd: "LDAP PRÓBA"
- **NEM** → Valóban rossz a jelszó, próbáld újra vagy reset

---

### 4. LDAP PRÓBA (Ha szükséges) (1 perc)

Ha az admin felületre sikerült bejelentkezni, de az API 401-et ad:

**Próbáld meg ezeket:**
```
1. Felhasználónév helyett:
   admin@domain.com
   DOMAIN\admin
   
2. Jelszó: ugyanaz

3. Futtasd a diagnostic scriptet újra
```

---

### 5. SPECIÁLIS KARAKTEREK ELLENŐRZÉSE (1 perc)

Ha a jelszó tartalmazhat speciális karaktereket:

**Lehetséges problémás karakterek:**
```
@ ! $ % # & ( ) " ' \ / | : ; , . < > ? * ^
```

**Megoldás:**
- Hozz létre egy új admin felhasználót **egyszerű** jelszóval (csak betűk és számok)
- Pl: `AdminPassword123`
- Próbáld az új felhasználóval

---

## 🎯 GYORS DECISION TREE

```
Diagnostic script hibát mutat?
│
├─ NEM, sikeres az auth
│  └─ ✓ Futtathatod az eredeti scriptet
│
└─ IGEN, 401-es hiba
   │
   ├─ Web felületre sikeres login?
   │  │
   │  ├─ NEM → Rossz a jelszó, reset szükséges
   │  │
   │  └─ IGEN
   │     │
   │     ├─ LDAP bejelentkezés volt?
   │     │  └─ Próbáld: admin@domain.com
   │     │
   │     └─ LOCAL felhasználó
   │        │
   │        ├─ Speciális karakterek a jelszóban?
   │        │  └─ Hozz létre új admin (alphanumerikus jelszó)
   │        │
   │        └─ Else → Kontaktálj Cisco support-ot
```

---

## 💾 FÁJLOK REFERENCIA

| Fájl | Mit Csinál | Mikor Futtatsd |
|------|-----------|-----------------|
| `catalyst_center_diagnostic.py` | 🔧 Diagnózis | Első 401-es hiba után |
| `catalyst_center_ip_pool_reservation.py` | 📝 IP pool reserválása | Után, ha diagnostic sikeres |
| `TROUBLESHOOTING_401.md` | 📖 Részletes útmutató | Ha diagnostic nem elegendő |

---

## ✅ CHECKLIST - 5 PERC ALATT

```
☐ Diagnostic script futtatva
☐ Output átnézve
☐ Admin web felületre bejelentkezve
☐ LDAP próbálva (ha szükséges)
☐ Új admin felhasználó létrehozva (ha szükséges)
☐ Diagnostic script újra futtatva
☐ Eredeti script futtatva
☐ IP pool sikeresen reserválva ✓
```

---

## 📞 HA MÉG MINDIG NEM MŰKÖDIK

```bash
1. Futtasd ezt és mentsd el az outputot:
   python catalyst_center_diagnostic.py > diagnostic_output.txt

2. Olvasd el ezt a fájlt:
   TROUBLESHOOTING_401.md

3. Ha arra sem talál rá:
   - Kontaktálj Cisco support-ot
   - Küldd el a diagnostic outputot
   - Add meg a CC verzióját
```

---

## 🎉 SIKER JELEI

Ha ezt látod:

```
[✓] CC elérhető: 10.8.11.100
[✓] Basic Auth sikeres!
[✓] IP pool sikeresen reserválva!
```

**KÉSZ! Az IP pool hozzáadódott a Catalyst Center-hez!** 🚀

---

**MOST PRÓBÁLD:** `python catalyst_center_diagnostic.py`
