# Race Conditions — PortSwigger LAB yechimlari (cheat sheet)

> Lab host = **example.com**. Asosiy metod: **single-packet attack** (Turbo Intruder / Burp
> Repeater tab group → "Send group in parallel"). Burp 2023.9+ kerak. HTTP/2.
> Qadam: collision bashorat → sequential benchmark → parallel probe → exploit.

### Limit overrun — APPRENTICE
Coupon/discount check'da race window → parallel yuborib bir necha marta qo'llaysan.
```
POST /cart/coupon ni duplicate → tab group → "Send group in parallel" (~20)
→ chegirma stack bo'ladi → jacket narxi < store credit
```
> Burp Pro: "Trigger race condition" custom action.

### Bypassing rate limits — PRACTITIONER
Login lockout counter'dan oldin ko'p urinish o'tkazasan.
```
Turbo Intruder single-packet: username=carlos, password = pozitsiya (wordlist)
→ bitta gate'da hammasini jo'nat → 302 = to'g'ri parol
```

### Multi-endpoint — PRACTITIONER
`POST /cart` + `POST /cart/checkout` ni parallel → to'lov balansdan oldin jacket qo'shiladi.
```
Tab group: POST /cart (productId=1) + POST /cart/checkout → "Send in parallel"
```
> Connection'ni warm qilish uchun avval homepage GET (keyin olib tashla).

### Single-endpoint — PRACTITIONER
Email o'zgartirish: sayt bitta pending email saqlaydi → parallel yuborib confirmation'ni
boshqa emailga chalkashtirsan.
```
Tab group: change-email=you@exploit.example.net + change-email=carlos@ginandjuice.shop
→ parallel → carlos confirmation link senga tushadi
```

### Partial construction — PRACTITIONER
Registration oqimida user yaratilayotgan paytda bo'sh token bilan confirm qilasan.
```
token[]=     (empty array — empty-value check'dan o'tadi)
Turbo Intruder single-packet: register (yangi username) + ko'p confirm (token[]=) bitta gate'da
→ Length bo'yicha sort → 200 success
```

### Exploiting time-sensitive vulnerabilities — PRACTITIONER
Reset token = timestamp hash → 2 ta sessiyadan parallel reset yuborib bir xil token olasan.
```
2 sessiya (alohida cookie/csrf): forgot-password you + forgot-password carlos → parallel
→ javob vaqtlari mos kelsa ikkisiga bir xil token → carlos link'ida username=carlos
```

---

### Eslatma
Tool: Turbo Intruder (single-packet template), Burp Repeater parallel group. Collision topish:
server-side state (cart, counter, pending email, token). Himoya: atomik operatsiya, DB lock,
idempotency. Umumiy: bu papka README.
