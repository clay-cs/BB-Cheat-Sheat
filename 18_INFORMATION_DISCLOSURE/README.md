# Information Disclosure

> Lab yechimlari (PortSwigger'ning 5 ta labi) → `LABS.md`. Bu fayl — to'liq nazariya + payload + tool.

## Nima bu? (tushuncha)
Ilova o'zi bilmagan holda maxfiy ma'lumotni oshkor qiladi — batafsil xato xabari (stack trace),
ochiq qolgan fayl (`.git`, `.env`, backup), debug sahifa, JS ichidagi secret, yoki ortiqcha API
javobi. O'zi kichik ko'rinadi, lekin bu ko'pincha boshqa, og'irroq hujumning **kaliti**.

**Ildiz sabab:** prod muhitda debug/verbose rejim qolgan, VCS/backup fayllar web root'da ochiq,
yoki dasturchi "buni hech kim topmaydi" deb o'ylagan. Ma'lumotning o'zi ba'zan to'g'ridan
compromise (credential), ba'zan keyingi qadam uchun yo'l ochadi (versiya → CVE, source → logic).

## Turlari
- **Verbose error / stack trace** — framework/versiya, SQL query, ichki yo'l oshkor bo'ladi.
- **Ochiq fayl/papka** — `/.git`, `/.env`, `/backup.zip`, `/.DS_Store`, `/actuator/*`, source backup.
- **Debug sahifa** — `phpinfo.php`, debug panel, `/actuator/env` → secret.
- **Client-side leak** — JS/HTML comment ichida API key, endpoint, credential.
- **VCS history** — `/.git` → o'chirilgan parol commit diff'da qoladi.
- **TRACE / method disclosure** — proxy qo'shgan ichki header (masalan auth IP) oshkor bo'ladi.

## Oqibatlar (IMPACT)
- **Secret/kalit/credential leak** → to'g'ridan compromise (DB, API, cloud).
- Texnologiya/versiya oshkori → aniq CVE exploit.
- `.git`/`.env`/source → butun logic va boshqa teshiklar ochiladi.
> O'zi ko'pincha Low, lekin chainga ulansa katta pul (`.env` → DB → ATO).

## Qayerdan qidiriladi

### Ochiq fayllar/papkalar
```
/.git/          → butun source (git-dumper)
/.env           → secret, DB cred, API key
/backup.zip  /db.sql  /dump.sql  /config.php.bak  /.DS_Store
/actuator/env  /actuator/heapdump   → Spring Boot secretlar
/swagger.json  /api-docs            → yashirin API
/server-status                       → Apache
```

### Xato xabar
Stack trace (framework+versiya+path), SQL xato, Django DEBUG, Flask `/console` → RCE.
Trigger: `id=abc`, `id[]=1`, maxsus belgi, juda uzun qiymat.

### JS / HTML
JS ichida API key, endpoint, internal URL; `.js.map` → original source; HTML comment.

## TOOLLAR

### git-dumper — ochiq .git ni to'liq tortish
```bash
git-dumper https://target.com/.git/ ./out
```
> `.git` ochiq bo'lsa — butun source kod va commit tarixini qaytadan tiklab beradi.

### nuclei exposures — ommaviy leak skani
```bash
nuclei -l live_hosts.txt -t ~/nuclei-templates/http/exposures/ -t ~/nuclei-templates/http/misconfiguration/
```
> `.env`, `.git`, actuator, swagger kabi yuzlab leak turini bir yo'la topadi.

### trufflehog — secret qidirish (JS/git/GitHub)
```bash
trufflehog github --org=target-org
```
> Kod va tarixdagi secretlarni topib, issuer API'da "hali ishlaydimi" deb tekshiradi.

### SecretFinder — JS ichidan kalit
```bash
python3 SecretFinder.py -i https://target.com/app.js -o cli
```
> JS bundle ichidan API key, token, AWS kalitni regex bilan sug'uradi.

### gitdorker — GitHub dork bilan leak
```bash
gitdorker -tf TOKENS.txt -q "target.com" -d dorks.txt
```
> GitHub'da `target.com` + "password/key" kombinatsiyalarini qidiradi.

### curl — actuator/heapdump qo'lda
```bash
curl -s https://target.com/actuator/env | jq && curl -s https://target.com/actuator/heapdump -o heap.bin
```
> Spring Boot ochiq bo'lsa — env va heapdump'dan secretlarni olasan.

## Chainga aylantirish
```
.git/source   → hardcoded secret, yashirin endpoint
.env/actuator → DB cred / SECRET_KEY → session forge / DB
stack trace   → aniq versiya → CVE
swagger       → yashirin API → IDOR
```

## PoC
Leak nimaga olib kelishini ko'rsat (secret → ATO, versiya → RCE CVE). Real PII dump qilma.

## Himoya
Prod'da debug o'chiq, umumiy xato sahifa, `.git`/`.env`/backup'ni web root'dan tashqarida
yoki bloklash, header'dan versiya olib tashlash, source map'ni prod'dan olib tashlash, vault.
