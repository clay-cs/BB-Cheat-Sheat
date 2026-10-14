# Business Logic Vulnerabilities

> Lab yechimlari (PortSwigger'ning 12 ta labi) → `LABS.md`. Bu fayl — to'liq nazariya + payload + tool.

## Nima bu? (tushuncha)
Kod yozilganidek **to'g'ri ishlaydi**, xato yo'q — lekin **mantiq** (biznes qoidasi) noto'g'ri
o'ylangan. Dastur foydalanuvchi "normal" yo'ldan borishini taxmin qiladi; sen esa taxmin
qilinmagan yo'ldan borasan (manfiy miqdor, qadamni o'tkazib yuborish, qiymatni ikki marta
ishlatish). Natijada ilova o'zini o'ziga qarshi ishlatasan.

**Ildiz sabab:** dasturchi foydalanuvchi xatti-harakatiga nisbatan noto'g'ri taxmin qilgan
("hech kim manfiy son kiritmaydi", "to'lovdan oldin bu qadam albatta bajariladi"). Scanner buni
**topolmaydi** — logikani faqat odam tushunadi. Shuning uchun raqobat kam, qiymat yuqori.

## Turlari (keng tarqalgan patternlar)
- **Narx/miqdor manipulyatsiyasi** — manfiy qty, client-side price, float/round xatosi.
- **Client-side control'ga ortiqcha ishonch** — price/discount client'dan keladi.
- **Workflow / qadamni o'tkazib yuborish** — to'lov qadamini sakrab order tasdiqlash.
- **Qoidani buzish** — kuponni ketma-ket/almashtirib ishlatish, limitni aylanish.
- **Exceptional/edge input** — juda uzun email (truncation), tur almashtirish, overflow.
- **Dual-use endpoint / weak isolation** — bir endpoint ikki maqsadga, izolyatsiya zaif.

## Oqibatlar (IMPACT)
- **Bepul/arzon xarid, cheksiz chegirma, "pul yaratish"**.
- To'lovni chetlab o'tish, limit/kvotalarni buzish.
- Auth logikasi buzilib → privilege escalation / ATO.
> Impact biznesga bog'liq — moliyaviy zarar aniq bo'lsa **High/Critical**. Avtomat topolmaydi → raqobat kam.

## Asosiy savol
Har qadamda so'ra: **"Developer nimani nazarda tutgan? Men boshqacha qilsam-chi?"**

## Keng tarqalgan patternlar
```
# Narx/miqdor manipulyatsiyasi
{"item":1,"qty":-5}          # manfiy miqdor → pul qaytadi
{"item":1,"price":0.01}      # narxni client yuboradi
qty: 0.0000001               # float/round xatosi

# Qadam o'tkazib yuborish
to'lov (step3) ni o'tkazib → step4 (yetkazib berish) → bepul mahsulot
email tasdiqlashsiz premium

# Holat manipulyatsiyasi
{"order_status":"paid"}
{"account_type":"premium"}
{"kyc_verified":true}

# Workflow abuse
refundni mahsulotni qaytarmasdan
1 referral kodidan cheksiz bonus
trial'ni email+1@ bilan qayta boshlash

# Ishonch chegarasi
client hisoblagan summani serverga yuborish
coupon'ni bir necha marta qo'llash
```

## Metodologiya
```
1. Jarayonni to'liq normal bajarib, har so'rovni Burp'da ko'r
2. Har parametr uchun: manfiy / nol / juda katta / float / bo'sh / yo'q qilsam?
3. Boshqa user ID / boshqa holat qiymati qo'ysam?
4. Qadamni tartibsiz / takror / o'tkazib bajarsam?
5. Parallel (race) yuborsam? (26-papka)
6. Client JS validatsiyani o'chirib ko'r — server ham tekshiradimi?
```

## TOOLLAR
> Bu yerda sehrli avtomat tool yo'q — miya asosiy tool. Lekin quyidagilar yordam beradi:

### Burp Repeater — har parametrni qo'lda o'ynash
```
Burp → Repeater → qiymatni manfiy/nol/katta qilib, javob farqini ko'r
```
> Logic bug'ni topishning asosiy quroli — bitta so'rovni yuzlab variantda qaytarasan.

### Burp Intruder — chegara qiymatlarni fuzzing
```
Intruder → narx/qty maydoniga -1, 0, 0.001, 999999999, null wordlist
```
> Qaysi qiymatda server boshqacha javob beradi — chegara bug'ini ko'rsatadi.

### Burp Logger / Autorize — workflow kuzatish
```
Logger++ → butun oqimdagi so'rovlar ketma-ketligini ko'r, qaysi tekshiruv server'da yo'q
```
> Qadamlar orasidagi "server tekshirmaydigan" joyni ko'rsatadi.

### ffuf — coupon/promo kod brute
```bash
ffuf -w coupons.txt -u https://target.com/apply -X POST -d "code=FUZZ" -H "Cookie: ..." -mr "applied"
```
> Mavjud chegirma kodlarini topadi (keyin logic bilan suiiste'mol qilasan).

## PoC
Normal oqim vs buzilgan oqimni qadam-qadam ko'rsat. Aniq biznes impact (bepul mahsulot,
cheksiz pul). Real zarar yetkazma — test rejim / minimal summa.

## Himoya
Har qadamni server tomonda tekshir (client'ga ishonma), narx/summa/holatni faqat server
hisoblasin, qiymat chegaralari (manfiy/katta rad), workflow holat mashinasi, muhim
operatsiyaga idempotency + race himoyasi.
