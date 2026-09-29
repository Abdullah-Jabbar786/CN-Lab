# CN Lab 5 — Revision Notes: SMTP, FTP, Wireshark

## 1. SMTP (Simple Mail Transfer Protocol)

**Purpose:** sends outgoing email from client → server, or server → server. **Sending only** — never used to retrieve mail.
**Port:** 25 (server-to-server relay), 587 (client submission, modern standard), 465 (deprecated, still seen).
**Runs over TCP** — email needs guaranteed, ordered delivery.

## 2. POP3 (Post Office Protocol v3)

**Purpose:** retrieves mail already sitting on the server, the "opposite half" of SMTP. **Pull-based** — the client must actively ask ("Receive"), mail isn't pushed to you automatically.
**Port:** 110.

**Mental model:** SMTP = mail carrier dropping letters into your mailbox. POP3 = you walking up and opening the box to take them out. Two separate actions, two separate protocols, one mailbox.

## 3. Packet Tracer Email Setup — command/config reference

**Server side** (Services → EMAIL): turn SMTP + POP3 both On, set a Domain Name (e.g. `fast.com`), add user accounts (username + password each).

**Client side** (PC → Desktop → Email → Configure Mail):
- Email Address — what appears in From/To fields (needs the domain, e.g. `user@fast.com`)
- Incoming/Outgoing Mail Server — both point to the mail server's IP
- **User Name** — the *login credential*, must exactly match what's registered on the server (no `@domain` suffix unless the server was configured that way — this is the #1 cause of "POP3 authentication failure")
- Password — must match exactly, including case

**Debugging "POP3 authentication failure":** always means the User Name or Password the client sent doesn't match what the server has on record. Check both sides side by side, character for character.

## 4. FTP (File Transfer Protocol)

**Purpose:** standardized file transfer between client and server.
**Port:** 21 (control connection).
**Runs over TCP.**

**The distinctive feature:** FTP uses **two separate connections** simultaneously:
- **Control connection** (port 21) — commands: login, list files, request a transfer
- **Data connection** — the actual file bytes, opened/closed per transfer

**Active vs Passive mode** (how the data connection gets set up):
| | Active | Passive |
|---|---|---|
| Who initiates data connection | Server → Client | Client → Server |
| Command used | `PORT M` | `PASV` |
| Firewall/NAT friendliness | Poor — client must accept inbound | Good — client always goes outbound |

Passive mode is the modern default precisely because most clients sit behind a router/firewall that blocks unsolicited inbound connections (same NAT logic as Lab 4).

**Response codes** (plaintext, numeric, similar spirit to HTTP status codes):
- `220` — server ready/greeting
- `331` — username OK, need password
- `230` — logged in successfully

**Key commands:**
- `ftp <IP>` — connect
- `USER <name>` / `PASS <password>` — login (sent in **plaintext** — a real security weakness of standard FTP)
- `put <file>` — upload (client → server)
- `dir` — list files on the server

**Permissions:** FTP accounts can be limited to specific rights (Read, Write, List, Delete, Rename) — not every account needs full control.

## 5. Wireshark

**What it is:** a real, industry-standard packet analyzer (not a simulation like Packet Tracer) — captures actual live traffic on a real network interface.

**Core workflow:**
1. Pick a capture interface (Wi-Fi, Ethernet, etc.)
2. Start capturing
3. Apply a **display filter** to cut noise — type it in lowercase in the filter bar, press Enter:
   - `tcp` — only TCP traffic
   - `dns` — only DNS traffic
   - `ip.addr == X.X.X.X` — only traffic to/from a specific IP
   - `ip.dst == X.X.X.X` — only traffic *to* a specific destination IP
   - `http` — only HTTP traffic

**The single most important takeaway from this lab:** visiting a plain `http://` (not `https://`) login page and capturing the traffic shows the **username and password in plaintext**, fully readable in the packet's form data. This is the concrete, hands-on proof of why HTTPS (Lab 4) matters — HTTP has zero encryption, anything submitted through it is visible to anyone capturing traffic on the path.

**Reading a packet:** select any packet → **Packet Details** pane shows the layer-by-layer breakdown (Ethernet → IP → TCP → HTTP/etc., directly mirrors the OSI model walkthroughs from Lab 4) → **Packet Bytes** pane shows the raw hex/ASCII of the actual bytes on the wire.

## High-Yield Viva Questions
1. Why can't SMTP handle both sending and receiving mail itself?
2. Why do "Incoming" and "Outgoing" mail server fields often point to different addresses in the real world, even though this lab used the same one for both?
3. Why does FTP need two connections when HTTP manages everything over one?
4. Why is passive mode generally more firewall-friendly than active mode?
5. What specifically makes an HTTP login page's credentials visible in Wireshark, and what would change if the site used HTTPS instead?
