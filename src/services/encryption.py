from __future__ import annotations

import base64


def _xor_bytes(data: bytes, key: bytes) -> bytes:
    if not key:
        raise ValueError("Encryption key cannot be empty.")
    return bytes(byte ^ key[index % len(key)] for index, byte in enumerate(data))


def encrypt_text(text: str, key: str) -> str:
    payload = text.encode("utf-8")
    encrypted = _xor_bytes(payload, key.encode("utf-8"))
    return base64.urlsafe_b64encode(encrypted).decode("ascii")


def decrypt_text(token: str, key: str) -> str:
    payload = base64.urlsafe_b64decode(token.encode("ascii"))
    decrypted = _xor_bytes(payload, key.encode("utf-8"))
    return decrypted.decode("utf-8")
# images
def _xor_bytes(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))

def decrypt_bytes(data: bytes, key: str) -> bytes:
    return _xor_bytes(data, key.encode("utf-8"))