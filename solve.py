
#!/usr/bin/env python3
import requests
import time
import json

URL = "https://pointeroverflowctf.com/challenges/consulting-room/oracle"
TOKEN = "Vrgg-aE9GESqwZA3TymZzFN5WCNOcR-P"

CT_HEX = (
    "82bfb61136c203a7bdbd0acf48adfd6e"
    "9997eb886cbb76112ba6ee0961ee8db9"
    "513a4bcb086d0a01d0d5d49c70a21927"
    "23b92a037eea00c7294bc0442895d8f66"
    "41b85406d19b4ea5994fb0781c6e2a3"
)

session = requests.Session()
session.headers.update({
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
})

last_request = 0.0
REQUEST_DELAY = 0.065

def oracle(data):
    global last_request

    wait = REQUEST_DELAY - (time.monotonic() - last_request)
    if wait > 0:
        time.sleep(wait)

    r = session.post(
        URL,
        json={"record": data.hex()},
        timeout=15,
    )
    last_request = time.monotonic()
    r.raise_for_status()

    result = r.json()
    if result.get("padding") not in ("valid", "invalid"):
        raise RuntimeError(f"Unexpected response: {result}")

    return result["padding"] == "valid"


def decrypt_block(prev, curr):
    intermediate = bytearray(16)
    crafted = bytearray(prev)

    for pos in range(15, -1, -1):
        pad = 16 - pos

        for j in range(pos + 1, 16):
            crafted[j] = intermediate[j] ^ pad

        found = False

        for guess in range(256):
            crafted[pos] = guess

            if not oracle(bytes(crafted) + curr):
                continue

            # Reject accidental longer-padding matches.
            if pos > 0:
                check = bytearray(crafted)
                check[pos - 1] ^= 1
                if not oracle(bytes(check) + curr):
                    continue

            intermediate[pos] = guess ^ pad
            found = True
            break

        if not found:
            raise RuntimeError(
                f"No valid byte found at position {pos}. "
                "Check the endpoint and ciphertext format."
            )

        print(f"Recovered byte {16-pos}/16", flush=True)

    return bytes(a ^ b for a, b in zip(intermediate, prev))


def main():
    ciphertext = bytes.fromhex(CT_HEX)

    if len(ciphertext) % 16 != 0:
        raise ValueError("Ciphertext length is not a multiple of 16")

    blocks = [
        ciphertext[i:i + 16]
        for i in range(0, len(ciphertext), 16)
    ]

    # Assumes the first block is the IV.
    plaintext = b""

    for i in range(1, len(blocks)):
        print(f"\nDecrypting block {i}/{len(blocks)-1}")
        plaintext += decrypt_block(blocks[i-1], blocks[i])

    print("\nRaw plaintext:", repr(plaintext))

    pad = plaintext[-1]
    if 1 <= pad <= 16 and plaintext.endswith(bytes([pad]) * pad):
        plaintext = plaintext[:-pad]

    print("Decoded plaintext:", plaintext.decode("utf-8", errors="replace"))

    for word in plaintext.decode("utf-8", errors="replace").split():
        if "{" in word and "}" in word:
            print("Possible flag:", word)


if __name__ == "__main__":
    main()
