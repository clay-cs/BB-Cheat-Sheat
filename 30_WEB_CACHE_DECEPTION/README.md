# Web Cache Deception

> Lab yechimlari (PortSwigger'ning 5 ta labi) → `LABS.md`. Bu fayl — to'liq nazariya + payload + tool.

## Nima bu? (tushuncha)
Cache odatda faqat **statik** fayllarni (`.css/.js/.jpg`) saqlaydi. Sen qurbonni shunday URL'ga
yetaklaysan: `/my-account/foo.css`. Cache "`.css` → statik, keshlayman" deydi; origin server esa
qo'shimchani e'tiborsiz qoldirib, baribir qurbonning **shaxsiy, auth'li** `/my-account` javobini
qaytaradi. Natijada qurbonning maxfiy javobi public cache'ga tushadi — keyin sen o'sha URL'ni
login'siz ochib, uning ma'lumotini o'qiysan.

**Ildiz sabab:** cache va origin server URL'ni **turlicha** talqin qiladi (qaysi qism "fayl", qaysi
"yo'l", qaysi "delimiter"). Shu nomuvofiqlik tufayli statik deb kesh qilingan narsa aslida dinamik,
shaxsiy javob bo'ladi.

> **Poisoning bilan farqi** (`16_WEB_CACHE_POISONING`): poisoning'da javobni **buzasan** va hammaga
> tarqatasan. Deception'da qurbonning **shaxsiy javobini** cache'ga tushirib, o'zing o'qiysan.

## Turlari (qaysi nomuvofiqlikdan foydalanish)
- **Path mapping** — `/my-account/foo.js` ni origin `/my-account`ga map qiladi.
- **Path delimiters** — origin `;`/`?` ni delimiter deb biladi, cache bilmaydi (`/my-account;foo.js`).
- **Origin server normalization** — origin encoded dot-segment (`..%2f`) ni resolve qiladi.
- **Cache server normalization** — cache dot-segment'ni resolve qiladi (teskarisi).
- **Exact-match cache rules** — aniq fayl (`/robots.txt`) qoidasini chalg'itish.

## Oqibatlar (IMPACT)
- **Boshqa odamning shaxsiy ma'lumotini olish** — profil, token, API key, PII.
- CSRF token leak → keyingi hujum (change-email → ATO).
- Session/ATO zanjiri.
> Sensitive data chiqsa odatda **High**.

## Asos: cache qoidasi vs app routing
Cache `.css/.js/.jpg` ko'rsa "static, keshlayman" deydi. App esa qo'shimchani e'tiborsiz
qoldirib, baribir `/account`ni ko'rsatadi.
```
GET /account/profile/x.css
→ cache: ".css → keshlayman"
→ app:   "/account/profile ni ko'rsataman"
→ natija: shaxsiy profil .css sifatida cache'ga tushdi
```

## Aniqlash
```http
GET /account/profile/x.css HTTP/1.1
Cookie: session=...
```
> Javob shaxsiy ma'lumot qaytardimi? Keshlandimi (`X-Cache: HIT`, `Age: N`)?
> Keyin login'siz (inkognito) o'sha URL'ni och — shaxsiy data ko'rinsa → ZAIF.

## Delimiter variantlari (bypass)
```
/account/profile.css
/account/profile/foo.css
/account/profile;foo.css        ; delimiter
/account/profile%2ffoo.css      encoded slash
/account/profile%00foo.css
/account/profile?x=1.css
```
Kengaytmalar: `.css .js .jpg .png .ico .svg .woff .txt .json`.

## Exploit oqimi
```
1. Zaif URL top: /account/x.css
2. Qurbonga shu linkni bostir (u login turibdi)
3. Qurbon ochganда, UNING javobi cache'ga tushadi
4. Sen (login'siz) o'sha URL'ni ochib, qurbon ma'lumotini olasan
```

## TOOLLAR

### curl — HIT/MISS qo'lda tekshirish (asosiy)
```bash
curl -sI "https://target.com/account/x.css" -H "Cookie: session=..." | grep -i cache
```
> Login holatda zaif URL keshlanadimi (`HIT`) — birinchi bosqich shu.

```bash
curl -s "https://target.com/account/x.css"
```
> Login'siz (cookie'siz) o'sha URL'da shaxsiy ma'lumot chiqsa — deception tasdiqlandi.

### web-cache-vulnerability-scanner (wcvs) — avtomat
```bash
wcvs scan -u https://target.com --cache-deception
```
> Ko'p delimiter/kengaytma variantini avtomat sinab, deception teshigini topadi.

### Burp Param Miner — delimiter/path probing
```
Burp → Param Miner → cache behavior'ni tekshirish uchun delimiter variantlari
```
> Cache qaysi qo'shimcha/delimiterni "static" deb qabul qilishini aniqlaydi.

### nuclei — ma'lum cache deception shablon
```bash
nuclei -u https://target.com -tags cache -t ~/nuclei-templates/http/misconfiguration/
```
> Ma'lum deception pattern'larni tez tekshiradi.

## Ehtiyot
O'z test akkauntingdan foydalan. Real user ma'lumotini keshlatma/o'qima.

## PoC
Login holatda zaif URL keshlanishini, keyin login'siz o'sha URL'da shaxsiy data
chiqishini ko'rsat. Impact: qaysi sensitive ma'lumot leak bo'ladi.

## Himoya
Cache'ni faqat haqiqatan static, sensitive bo'lmagan javobga qo'lla, sensitive'ga
`Cache-Control: no-store, private`, cache va origin path normalization bir xil, Content-Type
asosida keshlash (URL kengaytmasi emas).
