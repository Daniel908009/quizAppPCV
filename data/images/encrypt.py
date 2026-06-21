from pathlib import Path

SECRET_KEY = "quiz-app-secret-v1"


def xor_bytes(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def encrypt_file(path: Path, key: str) -> bytes:
    data = path.read_bytes()
    return xor_bytes(data, key.encode("utf-8"))


def main():
    folder = Path(__file__).parent

    for png in folder.glob("*.png"):
        encrypted = encrypt_file(png, SECRET_KEY)

        out_path = png.with_suffix(".bin")
        out_path.write_bytes(encrypted)

        print(f"Encrypted: {png.name} -> {out_path.name}")


if __name__ == "__main__":
    main()