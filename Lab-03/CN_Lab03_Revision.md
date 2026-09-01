# CN Lab 3 Revision — Socket Programming

---

## 1. Core Concepts (must know cold)

- **Socket** = endpoint of a bidirectional communication channel. Enables IPC (interprocess communication) across a network.
- **Berkeley sockets**: originated ARPANET 1971, standardized in BSD 1983. Still the underlying API today.
- **Client-server model**: server waits (listens) for connections; client initiates.

### TCP vs UDP

| | TCP | UDP |
|---|---|---|
| Full form | Transmission Control Protocol | User Datagram Protocol |
| Connection | Connection-oriented (handshake) | Connectionless |
| Reliability | Reliable, ordered delivery | No guarantee, no order |
| Socket type | `SOCK_STREAM` | `SOCK_DGRAM` |
| Send/Recv calls | `send()` / `recv()` | `sendto()` / `recvfrom()` |
| Use case | File transfer, web, chat | Streaming, DNS, fast/lossy-ok data |

---

## 2. TCP Connection Establishment (the sequence, memorize the order)

**Server:** `socket()` → `bind()` → `listen()` → `accept()` *(blocks here)*
**Client:** `socket()` → `connect()`

```
Server                          Client
socket()                        socket()
bind()
listen()
accept()  <---- connect() ------
  (blocks until client connects)
   |
   returns (new_socket, addr)
   |
read()/recv()  <---> write()/send()
write()/send() <---> read()/recv()
close()                         close()
```

**Key insight:** `accept()` returns a **brand-new socket** dedicated to that one client. The original listening socket keeps looping back to `accept()` for the next client — this is why a server can serve many clients sequentially without restarting.

---

## 3. Creating a Socket

```python
s = socket.socket(socket_family, socket_type, protocol=0)
```

| Param | Common values |
|---|---|
| `socket_family` | `AF_INET` (IPv4, most common), `AF_UNIX` (same-host only) |
| `socket_type` | `SOCK_STREAM` (TCP), `SOCK_DGRAM` (UDP) |
| `protocol` | usually `0` (auto-select) |

Default `socket.socket()` = `AF_INET` + `SOCK_STREAM` (TCP), which is why the lab examples don't pass args.

---

## 4. Method Cheat Sheet

**Server-side:**
| Method | Does |
|---|---|
| `s.bind((host, port))` | Attaches address to socket |
| `s.listen(n)` | Starts listening, `n` = max queued connections |
| `s.accept()` | Blocks, waits for client → returns `(conn_socket, addr)` |

**Client-side:**
| Method | Does |
|---|---|
| `s.connect((host, port))` | Actively connects to server |

**Shared (both sides, after connection):**
| Method | Does |
|---|---|
| `s.send(bytes)` | Send TCP data (must be **bytes**, use `.encode()`) |
| `s.recv(bufsize)` | Receive TCP data, returns bytes, use `.decode()` |
| `s.sendto(bytes, addr)` | Send UDP data |
| `s.recvfrom(bufsize)` | Receive UDP data → returns `(data, addr)` |
| `s.close()` | Closes the socket |
| `socket.gethostname()` | Local machine's hostname |
| `socket.gethostbyname(host)` | Hostname → IP |
| `socket.gethostbyaddr(ip)` | IP → hostname |
| `socket.getservbyport(port, proto)` | Port → service name (e.g. 80 → http) |

**⚠️ Golden rule:** sockets send/receive **bytes**, not strings.
`send()` → always `.encode()` first. `recv()` → always `.decode()` after.

---

## 5. Quick-Reference Code Templates

### A) Minimal TCP Server (single client)
```python
import socket

s = socket.socket()
s.bind(('localhost', 9999))
s.listen(5)
print("Waiting for connection...")

while True:
    c, addr = s.accept()
    print("Connected:", addr)
    data = c.recv(1024).decode()
    # ... process data ...
    c.send("response".encode())
    c.close()
```

### B) Minimal TCP Client
```python
import socket

s = socket.socket()
s.connect(('localhost', 9999))
s.send("hello".encode())
print(s.recv(1024).decode())
s.close()
```

### C) IP / Hostname Utilities
```python
import socket
hostname = socket.gethostname()
ip = socket.gethostbyname(hostname)

# hostname -> IP for any site
socket.gethostbyname("www.google.com")

# IP -> hostname
socket.gethostbyaddr("8.8.8.8")

# port -> service name
socket.getservbyport(80, 'tcp')   # 'http'
```

### D) Basic Port Scanner
```python
import socket, time

target_ip = socket.gethostbyname(input("Host: "))
for port in range(50, 500):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)          # avoid infinite hang on closed ports
    result = s.connect_ex((target_ip, port))   # returns 0 if open, no exception
    if result == 0:
        print(f"Port {port}: OPEN")
    s.close()
```
`connect_ex()` is safer than `connect()` for scanning — it returns an error code instead of raising an exception.

---

## 6. Patterns Likely to Show Up in Harder Exam Tasks

These weren't fully spelled out in the manual but are the natural "next level" — **know these**:

### a) Bidirectional / continuous chat (not just one send-recv)
Wrap in a loop on both sides so conversation continues until a stop condition (e.g. "bye"):
```python
while True:
    msg = input("You: ")
    s.send(msg.encode())
    if msg.lower() == "bye":
        break
    reply = s.recv(1024).decode()
    print("Server:", reply)
s.close()
```

### b) Handling multiple clients (threading)
A plain `while True: accept()` loop handles clients **one at a time** — the next client waits until the current one calls `close()`. For simultaneous clients, spin off a thread per connection:
```python
import socket, threading

def handle_client(c, addr):
    data = c.recv(1024).decode()
    c.send(f"Echo: {data}".encode())
    c.close()

s = socket.socket()
s.bind(('localhost', 9999))
s.listen(5)
while True:
    c, addr = s.accept()
    threading.Thread(target=handle_client, args=(c, addr)).start()
```

### c) UDP server/client (no connect/accept — connectionless)
```python
# UDP Server
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('localhost', 9999))
data, addr = s.recvfrom(1024)
s.sendto(b"got it", addr)

# UDP Client
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto(b"hello", ('localhost', 9999))
reply, addr = s.recvfrom(1024)
```
Note: no `listen()`/`accept()`/`connect()` — UDP just fires datagrams at an address.

### d) Robustness / error handling exam graders may check for
```python
try:
    s.bind(('localhost', 9999))
except socket.error as e:
    print("Bind failed:", e)
```
- `SO_REUSEADDR` avoids "Address already in use" when restarting a server quickly:
  ```python
  s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  ```
- Always wrap `connect()` in try/except for "connection refused" cases (server not running).
- Always `close()` sockets, even on error paths (or use `with socket.socket() as s:` — auto-closes).

### e) Sending structured data (not just plain strings)
If a task asks for multiple values (e.g. name + marks), either:
- Send as a delimited string: `f"{name},{marks}".encode()` then `.split(",")` on receive, or
- Use `json.dumps(dict).encode()` / `json.loads(data.decode())` for cleaner structured exchange — **more likely in a harder task**.

### f) Range/threshold-based response logic (like the grading scheme task)
Pattern: client sends a raw value → server maps it against a table of ranges/rules → sends back a derived result. General template:
```python
def evaluate(value, rules):
    for threshold, label in rules:
        if value >= threshold:
            return label
    return rules[-1][1]
```
Expect variations: temperature → category, marks → grade, price → discount tier, etc. Same shape, different table.

---

## 7. Common Mistakes That Cost Marks

1. Forgetting `.encode()` / `.decode()` → `TypeError`.
2. Calling `accept()` before `listen()`, or `listen()` before `bind()` — order matters.
3. Client trying to `connect()` before server has called `listen()`+`accept()` — get "connection refused."
4. Not closing sockets — causes "Address already in use" on re-run (fix: `SO_REUSEADDR`, or just wait, or change port).
5. Using `recv(1024)` assuming it always gets the *entire* message — fine for small lab data, but know that TCP doesn't guarantee one `send()` = one `recv()`.
6. Forgetting server `while True` loop → server handles one client then dies.
7. Mixing up `send`/`recv` (TCP) with `sendto`/`recvfrom` (UDP) — they are not interchangeable.

---

## 8. 30-Second Mental Recap Before Exam

> Server: **socket → bind → listen → accept (blocks) → recv/send → close**, wrapped in `while True` to keep serving.
> Client: **socket → connect → send/recv → close**.
> Bytes in, bytes out — always encode/decode.
> TCP = stream, connection-based, `send`/`recv`. UDP = datagram, connectionless, `sendto`/`recvfrom`.
> For "harder" tasks: think threading (multiple clients), loops (continuous exchange), JSON (structured data), and try/except (robustness) — these are the natural escalations from the basic manual examples.
