# API Testing (REST / OWASP API Top 10)

> Lab yechimlari (PortSwigger'ning 5 ta labi) → `LABS.md`. Bu fayl — to'liq nazariya + payload + tool.

## Nima bu? (tushuncha)
Zamonaviy saytlar API (REST/GraphQL) ustiga qurilgan — frontend faqat "chiroyli qobiq", asl ish
API endpoint'larda. API'larда avtorizatsiya ko'pincha **zaif**, chunki dasturchilar "bu endpointni
faqat bizning frontend chaqiradi" deb o'ylaydi. Sen esa endpointni to'g'ridan (docs, OPTIONS,
yashirin metodlar orqali) topib, UI cheklovlarsiz ishlatasan.

**Ildiz sabab:** API'da har obyekt/funksiya uchun server-side avtorizatsiya yo'q yoki client'ga
ishoniladi. Ortiqcha metodlar (`PATCH`/`DELETE`) ochiq qoladi, javoblar ortiqcha maydon beradi,
mass assignment orqali himoyalanmagan maydonlar yangilanadi. OWASP API Top 10 shularni sanaydi.

## Turlari (OWASP API Top 10'dan asosiylari)
- **BOLA / IDOR** (API1) — obyekt ID'sini almashtirib boshqa user ma'lumoti (eng ko'p to'laydi).
- **Broken auth** (API2) — zaif token/login.
- **BOPLA / Mass assignment** (API3) — `isAdmin:true`/`chosen_discount` qo'shib privilege/foyda.
- **BFLA** (API5) — admin funksiyasi (metod/endpoint) oddiy userга ochiq.
- **Excessive data exposure** — javobda kerak bo'lmagan sensitive maydon.
- **SSPP (Server-Side Parameter Pollution)** — `&`/`#` bilan backend query/path'ga parametr inject.
- **Unused/undocumented endpoint** — docs/OPTIONS orqali topilgan yashirin funksiya.

## Oqibatlar (IMPACT)
- **BOLA/IDOR** → boshqa user ma'lumoti (High, mass leak'ga chiqsa Critical).
- **BFLA** → admin funksiyasi oddiy user'da.
- **Mass assignment** → privilege escalation / tekin xarid.
- **SSPP** → reset token leak → ATO.
> Bitta BOLA = ko'pincha **High**, mass leak'ga chiqsa **Critical**.

## API topish
```bash
cat *.js | grep -Eo '"/api/[a-zA-Z0-9/_-]+"'
gau target.com | grep -Ei "/api/|/v1/|/v2/"
# Docs: /swagger.json /api-docs /openapi.json /graphql
```

## OWASP API Top 10 bo'yicha
```
API1 BOLA        GET /api/users/1338  (boshqa user → 06-papka)
API2 Auth        JWT (23), zaif API key, rate limit yo'q
API3 Mass asgn   PUT /api/user/me {"isAdmin":true,"balance":999999}
API3 Excessive   javobда password_hash, ssn, internal field
API5 BFLA        POST /api/admin/users (oddiy user token)
API7 SSRF        {"url":"http://169.254.169.254/"}  (10-papka)
API9 Inventory   /api/v1 (eski, himoyasiz) vs v2
```

## Checklist
```
□ Auth olib tashlasam ishlaydimi
□ Boshqa user token bilan boshqa resurs (BOLA)
□ Oddiy user admin endpoint (BFLA)
□ Ortiqcha field yuborsam (mass assignment)
□ Javobда ortiqcha sensitive field
□ Method swap (GET→PUT/DELETE/PATCH)
□ Content-Type swap (json↔xml↔form)
□ Eski API versiya (v1)
□ Rate limit / pagination limit
```

## Method bypass
```http
X-HTTP-Method-Override: DELETE
X-HTTP-Method: PUT
```

## TOOLLAR

### kiterunner — API endpoint bruteforce
```bash
kr scan https://target.com -w routes-large.kite
```
> Oddiy wordlist emas, API-ga xos (method+path+content-type) kombinatsiyalar bilan yashirin endpoint topadi.

### Arjun — yashirin parametr
```bash
arjun -u https://target.com/api/user -m POST
```
> API endpointidagi ko'rinmas parametrlarni (mass assignment uchun) topadi.

### Postman / Burp — asosiy qo'lda test
```
Swagger/OpenAPI'ni Postman'ga import qil → har endpointни auth bilan/siz sinaysan
```
> API oqimini tushunib, BOLA/BFLA'ni qo'lda topasan — asosiy ish shu.

### mitmproxy2swagger — trafikdan schema yasash
```bash
mitmproxy2swagger -i flows -o spec.yml -p https://target.com
```
> Ilova trafigini yozib olib, undan to'liq API spetsifikatsiyasini qaytaradi (yashirin endpointlar bilan).

### nuclei — API misconfig
```bash
nuclei -l api_urls.txt -t ~/nuclei-templates/http/ -tags api,exposure
```
> Ochiq swagger, himoyasiz endpoint, API key leak kabilarni ommaviy topadi.

## PoC
Eng kuchli: BOLA/BFLA → boshqa user/admin ma'lumoti yoki funksiyasi.

## Himoya
Har endpoint+har obyekt uchun authorization (object & function level), mass assignment'ga
allowlist (DTO), javobда faqat kerakli field, rate/pagination limit, eski API o'chirish.
