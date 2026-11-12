#!/usr/bin/env python3
"""Read-only ComfyUI REST/CORS/WebSocket check; never queues a job."""
import base64
import os
import socket
import sys
import urllib.parse
import urllib.request

url = os.environ.get("COMFY_URL", "http://127.0.0.1:8188").rstrip("/")
origin = os.environ.get("CANVAS_ORIGIN", "http://127.0.0.1:3000")
parsed = urllib.parse.urlparse(url)
if parsed.scheme != "http" or parsed.hostname != "127.0.0.1" or not parsed.port:
    sys.exit("COMFY_URL 必须是 http://127.0.0.1:<port>，避免误连公网接口")

try:
    req = urllib.request.Request(url + "/system_stats", headers={"Origin": origin})
    with urllib.request.urlopen(req, timeout=10) as resp:
        status = resp.status
        cors = resp.headers.get("Access-Control-Allow-Origin")
    print(f"HTTP /system_stats: {status}")
    print(f"CORS: {cors!r}")
    if status != 200 or cors != origin:
        sys.exit("HTTP 或 CORS 检查失败")

    key = base64.b64encode(os.urandom(16)).decode("ascii")
    with socket.create_connection(("127.0.0.1", parsed.port), timeout=10) as sock:
        sock.sendall((
            "GET /ws HTTP/1.1\r\n"
            f"Host: 127.0.0.1:{parsed.port}\r\n"
            f"Origin: {origin}\r\n"
            "Upgrade: websocket\r\nConnection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n"
        ).encode("ascii"))
        reply = sock.recv(4096).split(b"\r\n", 1)[0]
    print("WebSocket /ws:", reply.decode("ascii", "replace"))
    if b" 101 " not in reply:
        sys.exit("WebSocket 握手失败")
except (OSError, ValueError) as exc:
    sys.exit(f"连接失败：{exc}")

print("只读连接检查通过；未提交生成任务。")
