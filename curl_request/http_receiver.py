from http.server import BaseHTTPRequestHandler, HTTPServer
import os, re
from datetime import datetime

FILES_DIR = "./files"
os.makedirs(FILES_DIR, exist_ok=True)


def parse_multipart(data: bytes, boundary: str) -> list[tuple[str, bytes]]:
    sep = ("--" + boundary).encode()
    parts = data.split(sep)
    results = []
    for part in parts[1:]:
        if part in (b"--\r\n", b"--"):
            break
        if b"\r\n\r\n" not in part:
            continue
        header_raw, body = part.split(b"\r\n\r\n", 1)
        body = body.rstrip(b"\r\n")
        header_str = header_raw.decode(errors="replace")
        m = re.search(r'filename="([^"]+)"', header_str)
        fname = os.path.basename(m.group(1)) if m else "upload.bin"
        results.append((fname, body))
    return results


def normalize_newlines(data: bytes) -> bytes:
    """CRLF → LF 정규화"""
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def to_utf8(data: bytes) -> bytes:
    """CP949(EUC-KR) 또는 기타 인코딩 → UTF-8 변환. 이미 UTF-8이면 그대로 반환."""
    try:
        data.decode("utf-8")
        return data
    except UnicodeDecodeError:
        pass
    try:
        return data.decode("cp949").encode("utf-8")
    except UnicodeDecodeError:
        return data.decode("cp949", errors="replace").encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        ctype = self.headers.get("Content-Type", "")
        length = int(self.headers.get("Content-Length", 0))
        data = self.rfile.read(length)

        # multipart (curl -F "file=@...")
        if "multipart" in ctype:
            m = re.search(r'boundary=(.+)', ctype)
            boundary = m.group(1).strip() if m else ""
            for fname, content in parse_multipart(data, boundary):
                path = os.path.join(FILES_DIR, fname)
                with open(path, "wb") as f:
                    f.write(to_utf8(normalize_newlines(content)))
                print(f"[+] File saved : {path}")

        # 일반 텍스트 (curl -d @- 또는 curl -d "...")
        else:
            ts = datetime.now().strftime("%y%m%d")

            # URL path에 파일명이 있으면 그걸 사용 (예: /ipconfig.txt)
            url_fname = os.path.basename(self.path.lstrip("/"))
            fname = url_fname if url_fname else f"text_{ts}.txt"

            path = os.path.join(FILES_DIR, fname)
            content = to_utf8(normalize_newlines(data))

            # 파일명 지정된 경우 덮어쓰기, text_날짜 는 누적 append
            mode = "ab" if not url_fname else "wb"
            with open(path, mode) as f:
                f.write(content + (b"\n" if mode == "ab" else b""))
            preview = content[:300].decode(errors='replace')
            print(f"[+] Text saved : {path}")
            print(f"    Preview ---\n{preview}\n    ---")

        self.send_response(200)
        self.end_headers()

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    port = 12345
    print(f"[*] Listening on 0.0.0.0:{port}  →  saving to {FILES_DIR}/")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()