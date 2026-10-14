# Web Zaifliklar & Bug Bounty Cheat Sheet (o'zbekcha, ko'cha tilida)

Aka, bu yerda hamma narsa bor. Har bir zaiflik uchun alohida papka — ichida nima bu,
qayerdan topiladi, qanday uriladi, payloadlar, WAF bypass va **eng muhimi IMPACT** +
tool'lar (har biri: command + tushuntirish).

Qoida bitta: **faqat scope'dagi target.** Ruxsatsiz joyga tegma, DoS urma, real
odamning ma'lumotini o'g'irlama. Aks holda o'zing muammoga qolasan.

> **LAB cheat sheet'lar:** har bir papka ichida `README.md` (umumiy metod + payload + tool) va
> `LABS.md` (PortSwigger Web Security Academy'ning O'SHA kategoriyadagi HAMMA labining solution
> tahlili + tayyor payload) bor. Jami **277 lab**, 30 kategoriya. Domen misollarda `example.com`,
> exploit server `exploit.example.net`, Collaborator `COLLAB.example.net`. Lab'da haqiqiy
> `YOUR-LAB-ID...` host'ini qo'yasan. Lab START berib ovora bo'lmaysan — to'g'ridan solution.

---

## Zaifliklar ro'yxati

| # | Zaiflik | Papka |
|---|---------|-------|
| 01 | SQL Injection | [01_SQL_INJECTION](./01_SQL_INJECTION/) |
| 02 | XSS | [02_XSS](./02_XSS/) |
| 03 | CSRF | [03_CSRF](./03_CSRF/) |
| 04 | Clickjacking | [04_CLICKJACKING](./04_CLICKJACKING/) |
| 05 | DOM-Based | [05_DOM_BASED](./05_DOM_BASED/) |
| 06 | Access Control (IDOR) | [06_ACCESS_CONTROL](./06_ACCESS_CONTROL/) |
| 07 | Authentication | [07_AUTHENTICATION](./07_AUTHENTICATION/) |
| 08 | CORS | [08_CORS](./08_CORS/) |
| 09 | XXE | [09_XXE](./09_XXE/) |
| 10 | SSRF | [10_SSRF](./10_SSRF/) |
| 11 | HTTP Request Smuggling | [11_HTTP_REQUEST_SMUGGLING](./11_HTTP_REQUEST_SMUGGLING/) |
| 12 | OS Command Injection | [12_OS_COMMAND_INJECTION](./12_OS_COMMAND_INJECTION/) |
| 13 | SSTI | [13_SSTI](./13_SSTI/) |
| 14 | Path Traversal / LFI | [14_PATH_TRAVERSAL](./14_PATH_TRAVERSAL/) |
| 15 | WebSockets | [15_WEBSOCKETS](./15_WEBSOCKETS/) |
| 16 | Web Cache Poisoning | [16_WEB_CACHE_POISONING](./16_WEB_CACHE_POISONING/) |
| 17 | Insecure Deserialization | [17_INSECURE_DESERIALIZATION](./17_INSECURE_DESERIALIZATION/) |
| 18 | Information Disclosure | [18_INFORMATION_DISCLOSURE](./18_INFORMATION_DISCLOSURE/) |
| 19 | Business Logic | [19_BUSINESS_LOGIC](./19_BUSINESS_LOGIC/) |
| 20 | Host Header Attacks | [20_HOST_HEADER_ATTACKS](./20_HOST_HEADER_ATTACKS/) |
| 21 | OAuth | [21_OAUTH](./21_OAUTH/) |
| 22 | File Upload | [22_FILE_UPLOAD](./22_FILE_UPLOAD/) |
| 23 | JWT | [23_JWT](./23_JWT/) |
| 24 | Prototype Pollution | [24_PROTOTYPE_POLLUTION](./24_PROTOTYPE_POLLUTION/) |
| 25 | GraphQL | [25_GRAPHQL](./25_GRAPHQL/) |
| 26 | Race Conditions | [26_RACE_CONDITIONS](./26_RACE_CONDITIONS/) |
| 27 | NoSQL Injection | [27_NOSQL_INJECTION](./27_NOSQL_INJECTION/) |
| 28 | API Testing | [28_API_TESTING](./28_API_TESTING/) |
| 29 | Web LLM Attacks | [29_WEB_LLM_ATTACKS](./29_WEB_LLM_ATTACKS/) |
| 30 | Web Cache Deception | [30_WEB_CACHE_DECEPTION](./30_WEB_CACHE_DECEPTION/) |

---

# RECON — hujum yuzasini topish

Qoida: **recon tugamaydi.** Qancha asset topsang, shuncha teshik chiqadi. Avtomat
hammaga baravar, qo'l bilan topgan odam pul oladi. Shuncha gap.

## 0. Scope — birinchi shu

Scope'ni o'qimasdan bitta ham so'rov yuborma. `*.target.com` bo'lsa hamma subdomen
ichkarida. Out-of-scope'ni alohida faylga yozib qo'y va unga YAQIN YURMA.

---

## 1. Subdomain yig'ish — passiv (server sezmaydi)

### subfinder — eng tez passiv enum
```bash
subfinder -d target.com -all -recursive -o subs_subfinder.txt
```
> `-all` hamma manbani ishga soladi, `-recursive` topilgan subdan yana sub qidiradi.

### amass — chuqurroq, sekinroq
```bash
amass enum -passive -d target.com -o subs_amass.txt
```
> `-passive` target'ga to'g'ridan-to'g'ri so'rov yubormaydi, faqat ochiq bazalardan oladi.

### assetfinder — yengil va tez
```bash
assetfinder --subs-only target.com > subs_assetfinder.txt
```
> Faqat subdomenlarni chiqaradi, boshqa shovqinsiz.

### crt.sh — sertifikat loglaridan (juda samarali)
```bash
curl -s "https://crt.sh/?q=%25.target.com&output=json" | jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u > subs_crt.txt
```
> SSL sertifikatlarida ko'rinib qolgan ichki subdomenlarni tortib oladi.

### github-subdomains — GitHub'da ochilib qolganlar
```bash
github-subdomains -d target.com -t $GITHUB_TOKEN -o subs_gh.txt
```
> Dasturchilar kod ichiga yozib yuborgan subdomenlarni topadi.

### Hammasini birlashtir
```bash
cat subs_*.txt | sort -u > all_subs.txt && wc -l all_subs.txt
```
> Takrorlarni o'chirib, bitta toza ro'yxat yasaydi.

## 2. Subdomain — aktiv (bruteforce)

### puredns — tez DNS bruteforce
```bash
puredns bruteforce best-dns-wordlist.txt target.com -r resolvers.txt -w subs_brute.txt
```
> Wordlist'dagi har bir so'zni subdomen qilib DNS'da bor-yo'qligini tekshiradi.

### gotator — permutatsiya (dev, stage, admin variantlari)
```bash
gotator -sub all_subs.txt -perm permutations.txt -depth 1 -numbers 10 | puredns resolve -r resolvers.txt
```
> Topilgan subdomenlardan yangi variantlar yasaydi: `api` → `api-dev`, `api2` va h.k.

### dnsgen — o'xshash nom generatsiyasi
```bash
cat all_subs.txt | dnsgen - | dnsx -silent > subs_perm.txt
```
> Mavjud nomlardan aqlli variantlar yasab, tiriklarini filtrlaydi.

## 3. Tiriklarni ajratish

### dnsx — qaysi subdomen DNS'da bor
```bash
dnsx -l all_subs.txt -a -resp -o resolved.txt
```
> O'lik, resolve bo'lmaydigan subdomenlarni tashlab yuboradi.

### httpx — qaysi biri tirik web server
```bash
cat all_subs.txt | httpx -silent -title -status-code -tech-detect -web-server -cname -ip -o live_hosts.txt
```
> Har bir host'ning status kodi, sarlavhasi va texnologiyasini bir joyda beradi.

### 403/401 larni ajrat (bular bypass'ga arziydi)
```bash
cat live_hosts.txt | grep -E "40[13]|500"
```
> 403 = "kirish yo'q" degani, lekin ko'pincha bypass qilsa ochiladi (06-papka).

## 4. Port scan

### naabu — tez port scan
```bash
naabu -list resolved.txt -top-ports 1000 -o ports.txt
```
> Eng ko'p ishlatiladigan 1000 portni tez chamalab chiqadi.

### nmap — chuqur, versiya bilan
```bash
nmap -sV -sC -iL resolved.txt -oA nmap_scan
```
> `-sV` servis versiyasini, `-sC` default skriptlarni ishga soladi — CVE qidirishga asos.

> Noodatiy portlardagi web ham scope'da: 8080, 8443, 3000, 9000, 9200.

## 5. URL yig'ish

### gau — arxivdan URL
```bash
echo target.com | gau --subs > urls_gau.txt
```
> Wayback, OTX, urlscan arxividan eski URL va parametrlarni tortadi.

### waybackurls — Wayback Machine
```bash
waybackurls target.com > urls_wayback.txt
```
> Saytning eski versiyalaridagi URL'larni beradi (o'chirilgan endpointlar ham).

### katana — jonli crawler (JS ham o'qiydi)
```bash
katana -u live_hosts.txt -jc -kf all -d 5 -o urls_katana.txt
```
> `-jc` JS fayllarni ham parse qiladi, `-d 5` 5 daraja chuqur kiradi.

### Birlashtir + parametrlilarni ajrat
```bash
cat urls_*.txt | sort -u > all_urls.txt
cat all_urls.txt | grep "=" | sort -u > params_urls.txt
```
> `=` bor URL'lar = injection uchun oltin (test shulardan boshlanadi).

### qsreplace — payload joylashga tayyorla
```bash
cat params_urls.txt | qsreplace "FUZZ" | sort -u > fuzz_urls.txt
```
> Har parametr qiymatini `FUZZ` bilan almashtiradi — keyin payload quyasan.

## 6. gf bilan filtrlash (potensial teshiklar)

### gf — pattern bo'yicha ajratish
```bash
cat all_urls.txt | gf xss > maybe_xss.txt
cat all_urls.txt | gf sqli > maybe_sqli.txt
cat all_urls.txt | gf ssrf > maybe_ssrf.txt
cat all_urls.txt | gf redirect > maybe_redirect.txt
cat all_urls.txt | gf lfi > maybe_lfi.txt
```
> Har bir zaiflikka mos parametrlarni (`q=`, `url=`, `file=`) avtomat ajratadi.

## 7. JS analiz (bu yerda oltin ko'milgan)

### Avval JS fayllarni yig'
```bash
cat all_urls.txt | grep "\.js$" | sort -u > js_files.txt
```
> JS ichida yashirin API, token, endpoint bo'ladi.

### LinkFinder — JS ichidan endpoint
```bash
python3 linkfinder.py -i https://target.com/app.js -o cli
```
> JS kodidan `/api/...` yo'llarini regex bilan sug'urib oladi.

### SecretFinder — JS ichidan kalit/secret
```bash
python3 SecretFinder.py -i https://target.com/app.js -o cli
```
> API key, token, AWS kalit kabi secretlarni qidiradi.

### nuclei exposures — ochilib qolgan secretlar
```bash
cat js_files.txt | nuclei -t ~/nuclei-templates/http/exposures/
```
> Tayyor shablonlar bilan JS va javoblardagi secretlarni topadi.

### trufflehog — tekshirilgan live kalitlar
```bash
trufflehog filesystem ./downloaded_js/
```
> Topilgan kalitlar haqiqatan ishlaydimi — issuer API'da tekshiradi.

## 8. Directory / fayl topish

### ffuf — directory bruteforce
```bash
ffuf -u https://target.com/FUZZ -w raft-medium-directories.txt -mc 200,204,301,302,307,401,403 -o ffuf.json
```
> `FUZZ` o'rniga wordlistdagi so'zlarni qo'yib, mavjud yo'llarni topadi.

### feroxbuster — rekursiv, tez
```bash
feroxbuster -u https://target.com -w wordlist.txt -x php,bak,zip,json
```
> Topilgan papka ichiga o'zi kirib, `.bak/.zip` kabi kengaytmalarni ham sinaydi.

### arjun — yashirin parametr topish
```bash
arjun -u "https://target.com/api/user" -m GET
```
> URL'da ko'rinmaydigan maxfiy parametrlarni topadi (IDOR/SSRF uchun bebaho).

### x8 — parametr topish (alternativ)
```bash
x8 -u "https://target.com/" -w params.txt
```
> Katta wordlist bilan yashirin GET/POST parametrlarni brute qiladi.

## 9. Fingerprint + WAF

### whatweb — texnologiya aniqlash
```bash
whatweb https://target.com
```
> CMS, framework, server versiyasini aytadi — keyin aniq CVE qidirasan.

### wafw00f — WAF bor-yo'qligi
```bash
wafw00f https://target.com
```
> Oldida Cloudflare/Akamai bormi — payloadni shunga moslaysan.

## 10. Avtomat skan

### nuclei — asosiy avtomat tool
```bash
nuclei -l live_hosts.txt -t ~/nuclei-templates/ -severity critical,high,medium -rl 50 -o nuclei.txt
```
> `-rl 50` sekundiga 50 so'rov — serverni urmaslik uchun tiyib turadi.

### nuclei — faqat CVE
```bash
nuclei -l live_hosts.txt -tags cve -o cve.txt
```
> Ma'lum zaifliklarni (CVE) tez tekshiradi.

### subzy — subdomain takeover
```bash
subzy run --targets all_subs.txt
```
> Egasiz qolib ketgan (dangling) subdomenlarni egallab olish mumkinligini tekshiradi.

## 11. Cloud & Git

### cloud_enum — ochiq bucketlar
```bash
cloud_enum -k target -k target.com
```
> AWS S3, Azure, GCP'dagi ochiq saqlanish joylarini qidiradi.

### s3scanner — S3 bucket
```bash
s3scanner scan --bucket target-backups
```
> Bucket ochiq o'qish/yozishga ruxsat berganmi — tekshiradi.

### trufflehog github — org leaklari
```bash
trufflehog github --org=target-org
```
> Butun GitHub tashkilotining kodidagi live secretlarni qidiradi.

---

# KENGAYTIRILGAN ENUMERATION — ko'proq tool va usul

> Yuqoridagi 0–11 = asosiy quvur. Pastdagisi = chuqurroq, ko'proq surfaces. Kombinat qil,
> hech biri "yetarli" emas. **Avtomat hammaga baravar — qo'l + noyob metod pul oladi.**

## 12. ASN & IP range — org darajasida (katta surface)

### asnmap — organizatsiya ASN → IP bloklar
```bash
asnmap -d target.com | dnsx -ptr -resp-only | httpx -silent
```
> Kompaniyaning butun ASN'idagi IP diapazonini chiqaradi — subdomendan tashqari assetlar.

### amass intel — org nomidan domen/ASN
```bash
amass intel -org "Target Inc" 
amass intel -asn 12345 -whois
```
> Tashkilot nomi/ASN'dan tegishli domenlarni topadi (apex domenlar kengayadi).

### whois + reverse whois — bog'liq domenlar
```bash
whois target.com | grep -iE "org|net|registrant"
```
> Registrant email/org bo'yicha boshqa domenlarni (whoxy/reverse whois) qidirish uchun asos.

### mapcidr + dnsx — IP blokni resolve
```bash
echo "192.0.2.0/24" | mapcidr | dnsx -ptr -resp-only
```
> CIDR'ni IP'larga yoyib, PTR (reverse DNS) bilan host nomlarini chiqaradi.

## 13. Internet-wide qidiruv (Shodan/Censys/favicon)

### favicon hash — bir xil faviconli hamma host
```bash
# favicon murmur3 hash hisobla, keyin Shodan'da qidir
curl -s https://target.com/favicon.ico | python3 -c "import mmh3,sys,codecs,base64;print(mmh3.hash(codecs.encode(base64.b64encode(sys.stdin.buffer.read()))))"
# Shodan: http.favicon.hash:<HASH>
```
> Bir xil favicon = odatda bir xil org/panel. Yashirin, CDN ortidagi origin'larni ochadi.

### shodan CLI — ochiq servis/panel
```bash
shodan search "ssl.cert.subject.cn:target.com" --fields ip_str,port
shodan search "http.title:'Admin' org:'Target Inc'"
```
> Portlar, panellar, versiyalar — passiv, server sezmaydi. `Hostname`/`org`/`ssl` filtrlari zo'r.

### censys / fofa / zoomeye — alternativ
```
censys: services.tls.certificates.leaf_data.subject.common_name: target.com
fofa:   domain="target.com" || cert="target.com"
```
> Har biri boshqa narsani ko'radi — uchtasini ham sina (origin IP, eski panel topiladi).

### uncover — bitta CLI, hamma engine
```bash
uncover -q "ssl:target.com" -e shodan,censys,fofa -silent | httpx -silent
```
> Shodan/Censys/Fofa'ni bitta buyruqda so'rab, tirik host'larni beradi.

## 14. Dorking — Google & GitHub (qo'lda oltin)

### Google dork
```
site:target.com -www
site:target.com ext:php | ext:bak | ext:sql | ext:log | ext:env
site:target.com inurl:(login|admin|dashboard|api|redirect|debug)
site:target.com intitle:"index of"
site:*.target.com inurl:?
site:pastebin.com target.com
```
> Indekslangan maxfiy fayl, panel, parametrli URL — bepul, tez.

### GitHub dork (leak qidirish)
```
org:target-org password
"target.com" api_key
"target.com" filename:.env
"target-internal" AWS_SECRET
```
> Dasturchi kod ichiga yozib yuborgan secret/endpoint. `gitdorks_go` avtomatlashtiradi:
```bash
gitdorks_go -gd dorks.txt -t $GITHUB_TOKEN -ri -o gitleaks.txt -tf target_list.txt
```

### shodan/google dorking resurslari
```
GHDB (exploit-db), Shodan query ro'yxatlari, lampyre/pimeyes OSINT.
```

## 15. VHost & origin IP (CDN/WAF ortidan o'tish)

### ffuf — virtual host brute
```bash
ffuf -u https://target.com -H "Host: FUZZ.target.com" -w subdomains.txt -fs 0
```
> Bitta IP'da yashiringan vhost'larni (DNS'da ko'rinmaydigan) topadi. `-fs` — bir xil hajmni filtrla.

### gobuster vhost
```bash
gobuster vhost -u https://target.com -w subdomains.txt --append-domain
```
> Xuddi shu, alternativ. Dev/staging vhost ko'pincha himoyasiz.

### origin IP topish (Cloudflare bypass)
```bash
# 1) DNS history
curl -s "https://securitytrails.com/..."   # yoki viewdns.info, dnshistory
# 2) SSL cert orqali Shodan/Censys
shodan search "ssl:target.com" --fields ip_str
# 3) subdomen origin'ni oshkor qilsa
dnsx -l all_subs.txt -a -resp-only | anew ips.txt
# 4) to'g'ridan IP'ga Host bilan ur
curl -s -H "Host: target.com" https://<origin_ip>/ -k
```
> WAF faqat domen oldida turadi. Origin IP topilsa — to'g'ridan urib WAF'ni aylanasan.

### cf-check / cloudflail — avtomat origin
```bash
cloudfail --target target.com
```
> DNS history + bruteforce bilan Cloudflare ortidagi real IP'ni qidiradi.

## 16. Screenshot / visual recon (minglab hostni ko'z bilan)

### gowitness — tez skrinshot
```bash
gowitness scan file -f live_hosts.txt --screenshot-path ./shots/
```
> Har hostning rasmini oladi — login panel, default sahifa, xato'ni ko'z bilan tez ajratasan.

### aquatone / eyewitness — alternativ
```bash
cat live_hosts.txt | aquatone -out ./aquatone_report
```
> HTML report yasaydi — o'xshashlarni guruhlab, qiziqni darrov ko'rasan.

## 17. Content discovery — ko'proq (fayl/papka/API)

### dirsearch — aqlli, kengaytma bilan
```bash
dirsearch -u https://target.com -e php,asp,aspx,jsp,html,js,zip,bak,sql,json,log -x 404,403
```
> Recursive, rang bilan. `-x` keraksiz statuslarni tashlaydi.

### gobuster dir — tez Go
```bash
gobuster dir -u https://target.com -w raft-large-words.txt -x php,bak,old,zip -t 50
```

### kiterunner — API endpoint (routes-level)
```bash
kr scan https://target.com/api -w routes-large.kite -x 20
```
> Oddiy wordlist emas, Swagger/API route patterns bilan — yashirin API metodlarini topadi.

### feroxbuster recursion + auto-tune
```bash
feroxbuster -u https://target.com -w wordlist.txt -r --auto-tune -C 404,403
```
> `-r` redirectlarni kuzatadi, rate'ni o'zi moslaydi.

### backup/config maxsus sweep
```bash
ffuf -u https://target.com/FUZZ -w <(printf '.git/HEAD\n.env\n.svn/\nbackup.zip\nconfig.php.bak\n.DS_Store\nwp-config.php.bak\n') -mc 200
```
> Eng tez-tez qolib ketadigan maxfiy fayllarni nuqtali urish (18-papka).

## 18. URL yig'ish — chuqurroq

### waymore — gau'dan kengroq arxiv
```bash
waymore -i target.com -mode U -oU urls_waymore.txt
```
> Wayback + Common Crawl + URLScan + VirusTotal — eng ko'p eski URL.

### gospider / hakrawler — jonli crawl
```bash
gospider -s https://target.com -d 3 -c 10 --other-source | anew urls_crawl.txt
echo https://target.com | hakrawler -d 3 -subs
```
> JS, form, link'larni jonli kezib yig'adi (katana'ga qo'shimcha manba).

### uro — URL'ni tozalash/dedup
```bash
cat all_urls.txt | uro > clean_urls.txt
```
> Bir xil pattern URL'larni (`?id=1`, `?id=2`...) bittaga qisqartiradi — shovqin ketadi.

### unfurl — URL qismlarini ajratish
```bash
cat all_urls.txt | unfurl -u keys | sort -u      # hamma parametr nomlari
cat all_urls.txt | unfurl -u domains | sort -u   # hamma domenlar
```
> Parametr nomlari, path, domenlarni ajratib tahlilga tayyorlaydi.

## 19. JS analiz — chuqurroq (secret + endpoint)

### getJS / subjs — JS fayllarni yig'ish
```bash
cat live_hosts.txt | getJS --complete | anew js_files.txt
cat live_hosts.txt | subjs | anew js_files.txt
```
> Sahifalardagi hamma `<script src>` ni to'liq URL qilib chiqaradi.

### jsluice — JS'dan URL + secret (eng kuchli)
```bash
cat js_files.txt | while read u; do curl -s "$u" | jsluice urls; curl -s "$u" | jsluice secrets; done
```
> AST bilan tahlil qiladi — regex'dan aniqroq, yashirin endpoint/token topadi.

### xnLinkFinder — endpoint + parametr
```bash
python3 xnLinkFinder.py -i js_files.txt -sf target.com -o endpoints.txt -op params.txt
```
> JS'dan endpoint VA parametrlarni birga chiqaradi (arjun/ffuf uchun yoqilg'i).

### Mantra / nuclei exposures — token sweep
```bash
cat js_files.txt | mantra
cat js_files.txt | nuclei -t ~/nuclei-templates/http/exposures/tokens/
```
> JS ichidagi API key/token/credential'ni tez ajratadi.

## 20. Yashirin parametr — ko'proq

### ParamSpider — arxivdan parametr
```bash
paramspider -d target.com
```
> Wayback'dan domenning hamma parametrli URL'ini tortadi (passiv, tez).

### Arjun — JS'dan topilgan endpointlarга
```bash
arjun -i endpoints.txt -m GET,POST -oT arjun_out.txt
```
> xnLinkFinder topgan endpointlarga yashirin parametr brute (IDOR/mass-assignment yo'li).

### Burp Param Miner — header/cookie/param (eng chuqur)
```
Burp → Param Miner → "Guess headers / params / cookies"
```
> Cache poisoning va yashirin funksiya uchun eng ishonchli (16, 20-papka).

## 21. Secret & Git — ko'proq

### gitleaks — git repo/history
```bash
gitleaks detect --source ./repo -v
```
> Commit tarixidagi secret'ni (o'chirilgan bo'lsa ham) topadi.

### noseyparker — ulkan history'da tez
```bash
noseyparker scan ./repo && noseyparker report
```
> Juda katta repo/history'ni tez skanerlaydi (trufflehog sekin qolsa).

### github-search / gitdorks — org bo'ylab
```bash
gitdorks_go -gd dorks.txt -t $GITHUB_TOKEN -tf targets.txt
```
> Butun org kodida dork bo'yicha leak qidiradi (14-bo'lim bilan juft).

## 22. Email & xodim OSINT (spray/phishing scope bo'lsa)

### theHarvester — email/host/xodim
```bash
theHarvester -d target.com -b all
```
> Qidiruv engine + CT loglardan email, subdomen, xodim nomlarini yig'adi.

### email pattern + dmarc/spf
```bash
dig TXT target.com | grep -iE "spf|dmarc"
```
> Email siyosatini ko'rib, spoofing/takeover imkonini baholaysan (scope'da bo'lsa).

## 23. Mobile app — yangi surface (scope'da APK bo'lsa)

### apktool + grep — endpoint/secret
```bash
apktool d app.apk -o app_src/
grep -rEn "https?://|api_key|secret|firebaseio|s3\.amazonaws" app_src/
```
> APK ichida web'da ko'rinmaydigan API, base URL, hardcoded key bo'ladi (katta surface).

### jadx — decompile + o'qish
```bash
jadx -d app_out/ app.apk
```
> Kodni o'qib, imzolash/endpoint mantig'ini tushunasan (28-papka API hunt).

## 24. Wordlistlar (enumeration yoqilg'isi)

```bash
# SecLists — standart
git clone https://github.com/danielmiessler/SecLists
# Assetnote — eng yangi, real traffic'dan
wget https://wordlists-cdn.assetnote.io/data/manual/best-dns-wordlist.txt
# cewl — target saytdan maxsus wordlist
cewl -d 2 -m 5 https://target.com -w custom_words.txt
```
> Content/DNS discovery sifati wordlist'ga bog'liq. Assetnote + SecLists + cewl (target-specific).

## 25. 403 / 401 bypass toollari (recon'da ko'p chiqadi)

### nomore403 / byp4xx / dontgo403
```bash
nomore403 -u https://target.com/admin
byp4xx https://target.com/admin
```
> Header, path encoding, method, case bilan 40+ bypass avtomat sinaydi (06-papka jadvali).

## 26. Monitoring — uzluksiz recon (yangi asset = yangi bug)

### notify — yangi topilma → Telegram/Slack
```bash
subfinder -d target.com -silent | anew subs.txt | notify
```
> Yangi subdomen chiqsa darhol xabar beradi — birinchi bo'lib urasan.

### cron bilan avtomat kuzatuv
```bash
# har kuni: yangi sub → httpx → nuclei → notify
0 */6 * * * subfinder -d target.com -silent | anew ~/subs.txt | httpx -silent | nuclei -silent | notify
```
> Dastur yangi feature/subdomen chiqarganda birinchi sen ko'rasan = raqobatdan oldinda.

### JS change monitor
```bash
# JS hash'ini saqlab, o'zgarganini ushla (yangi endpoint = yangi hujum)
cat js_files.txt | while read u; do curl -s "$u" | sha1sum; done > js_hashes_new.txt
diff js_hashes_old.txt js_hashes_new.txt
```

## 27. All-in-one frameworklar (tez start uchun)

```bash
reconftw -d target.com -r            # to'liq avtomat recon (hammasini bitta skript)
osmedeus scan -t target.com          # modular, katta scope
# reNgine — web UI'li recon platform (Docker)
nuclei -l live_hosts.txt -t ~/nuclei-templates/ -as   # automatic scan (tech'ga mos shablon)
```
> Tez boshlash uchun yaxshi, lekin hamma shuni ishlatadi — **farqni qo'l bilan qilasan.**

## 28. Foydali one-liner'lar

```bash
# Butun quvur: sub → tirik → URL → gf → nuclei
subfinder -d target.com -all -silent | dnsx -silent | httpx -silent | \
  katana -jc -silent | tee all.txt | nuclei -silent -severity high,critical | notify

# anew — faqat yangi qatorni qo'shadi (takror yo'q)
cat new.txt | anew all_subs.txt

# interlace — istalgan toolni parallel yugurtirish
interlace -tL hosts.txt -c "nuclei -u _target_ -o _output_" -o ./out

# qsreplace bilan ommaviy XSS probe
cat params_urls.txt | qsreplace '"><script>alert(1)</script>' | httpx -silent -mr "<script>alert(1)"
```

---

## Workflow — qisqa ketma-ketlik
```
scope → subfinder/amass/crt.sh + asnmap/shodan/favicon → puredns/gotator → dnsx/httpx →
naabu/nmap → gau/waymore/katana/gospider → uro/unfurl → gf/arjun/paramspider →
getJS/jsluice/xnLinkFinder → ffuf/dirsearch/kiterunner → gowitness (ko'z bilan) →
whatweb/wafw00f → nuclei/subzy/takeover → QO'L BILAN HUNT (zaiflik papkalari) → notify monitoring
```

## Qayerdan boshlash (pul bo'yicha)
1. **IDOR / Access Control** — oson, ko'p to'laydi (06)
2. **Auth / OAuth / JWT** — account takeover = katta pul (07, 21, 23)
3. **SSRF** — cloud metadata chiqsa Critical (10)
4. **XSS** — stored bo'lsa ATO zanjiri (02)
5. **Business Logic** — avtomat topolmaydi, faqat miya (19)

## Chaining — zanjirlasang pul oshadi
```
IDOR          → account takeover
SSRF          → cloud metadata → AWS kalit → hamma narsa sizniki
Open redirect → OAuth token o'g'irlash
Stored XSS    → admin cookie → admin panel
File upload   → RCE
LFI           → RCE (log poisoning / php filter chain)
```
