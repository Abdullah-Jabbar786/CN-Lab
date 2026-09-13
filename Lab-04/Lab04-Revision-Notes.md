# CN Lab 4 — Revision Notes: HTTP/HTTPS, DNS, Routers

## 1. Routers — the core concept

**Problem solved:** switches connect devices *within* one network (Layer 2, MAC-based). A router connects *separate* networks and decides how to move packets between them (Layer 3, IP-based). Without a router, two differently-addressed networks simply cannot reach each other.

**How it works:**
1. Operates at **Layer 3** (Network layer)
2. Reads the packet's **destination IP**
3. Checks its **routing table** for the best path
4. Forwards to the next hop or directly to the destination network

**Key functions:** Path determination (RIP/OSPF/EIGRP), Packet forwarding, Traffic filtering (ACL), Network segmentation.

## 2. Router CLI configuration — command reference

| Command | What it does |
|---|---|
| `enable` | User mode → privileged mode (like `sudo`) |
| `config t` | Privileged mode → global configuration mode |
| `interface <name>` | Enter config mode for a specific physical port |
| `ip address <ip> <mask>` | Assign IP + subnet mask to that interface |
| `no shut` | Administratively turn the interface **on** (interfaces default to off) |
| `exit` | Back out one config level |
| `show ip interface brief` | List all interfaces, their IPs, and up/down status |
| `show running-config` | View the full current configuration |

**Critical gotcha:** forgetting `no shut` leaves a correctly-addressed interface that still won't pass traffic, status stays "administratively down" until this is run.

**Every device behind a router needs a Default Gateway** set to that router's interface IP on their side, otherwise they have no way to send traffic outside their own subnet (confirmed by the "no route to cross-network host" symptom → 100% ping loss until gateway is set).

**TTL as proof of routing:** a ping within the same network shows `TTL=128`; a ping that crossed one router shows `TTL=127` (decrements by 1 per hop). This is direct evidence a packet actually traveled through a router.

## 3. HTTP vs HTTPS

| | HTTP | HTTPS |
|---|---|---|
| Port | 80 | 443 |
| Security | None | Encrypted (SSL/TLS) |
| Certificate | Not required | Required (signed or self-issued) |

**HTTPS = HTTP + TLS/SSL.** The encryption prevents anyone intercepting the traffic (ISP, same-network attacker) from reading the actual content, including form data/passwords. Certificates let the client verify the server's identity before trusting it.

## 4. HTTP Status Codes

**4xx = client's fault** (something about the request was wrong):
- 400 Bad Request — malformed request
- 401 Unauthorized — authentication required/failed
- 403 Forbidden — identified but not permitted (auth won't help, unlike 401)
- 404 Not Found
- 408 Request Timeout

**5xx = server's fault** (client did nothing wrong):
- 500 Internal Server Error — generic failure
- 501 Not Implemented — server can't handle this method
- 502 Bad Gateway — this server, acting as proxy, got a bad response from upstream
- 503 Service Unavailable — overloaded/down for maintenance (temporary)

**Exam trap:** 401 vs 403 — 401 says "prove who you are," 403 says "I know who you are, still no."

## 5. Caching Header

**`Expires`** header = sets a "best before" date on a cached resource. After that date, the browser must re-fetch from the server instead of trusting its local cache.
(Modern alternative: `Cache-Control: max-age=...`, relative rather than absolute — but `Expires` is the direct answer to "best before date.")

## 6. PUT vs POST

- **POST**: creates a new resource each time — calling it twice creates two resources. Not idempotent.
- **PUT**: replaces/updates a resource at a known location — calling it multiple times with the same data gives the same end result. Idempotent.

## 7. DNS

**Problem solved:** routing works by IP, humans remember names. DNS translates names → IPs.

**Record types:**
| Record | Purpose |
|---|---|
| A Record | Maps a domain name directly to an IP address |
| CNAME | Alias pointing to another domain name (not directly to an IP) — update one A record, every CNAME pointing at it stays correct |
| NS | Identifies which DNS server is authoritative for a zone |
| SOA | Administrative metadata about the zone (who manages it, refresh interval, etc.) |

**DNS resolution always happens before the actual connection** — confirmed by simulation event lists always showing DNS query/response *before* the TCP/HTTP exchange begins.

**DNS runs over UDP** (Layer 4), not TCP — a single query/response doesn't need TCP's connection overhead.

**Cross-router DNS** takes more hops than same-network DNS (query must climb switch layers → router → descend the other side's switch layers), directly visible by comparing event list hop counts.

## 8. Packet Tracer Simulation Mode — workflow

1. Toggle **Simulation mode** (bottom right)
2. **Edit Filters** → uncheck all → check only the protocol you care about (DNS, HTTP, HTTPS)
3. Trigger the action (browse to a URL, etc.)
4. Click **Capture/Forward** repeatedly to step through packet-by-packet
5. Click any packet in the Event List → opens **PDU Information** (OSI Model / Inbound / Outbound PDU Details tabs)
6. Note: ARP traffic often still appears even when filtered for something else — it's a prerequisite step (resolving MAC addresses) that happens before most other traffic; identify it by destination IP and the "ARP process" note in its PDU.

## 9. Task Summary (what was built)

| Task | What it demonstrates |
|---|---|
| 1 | DHCP auto-assigning IPs + DNS A record + captured DNS query/response on a flat network |
| 2 | Router connecting two subnets, cross-network ping (TTL=127 proof), DNS resolution across the router |
| 3 | `Expires` header — best-before caching |
| 4 | PUT vs POST — idempotency difference |
| 5 | A Record + CNAME Record configured together, domain resolution via alias |
| 6 | Hosting a custom page, inspecting HTTP response headers in simulation mode |
| 7 | Router + tracert across two networks — verifying the path hop by hop |
| 8 | NS + SOA records — zone authority and administrative metadata |
| 9 | `show running-config` — verifying interface IPs directly from router config |

## High-Yield Viva Questions
1. Why must `no shut` be run even after assigning an IP to an interface?
2. Why does a missing default gateway cause 100% ping loss to a different subnet, but not to the same subnet?
3. What does a TTL of 127 (instead of 128) tell you about a ping's path?
4. Why does DNS use UDP instead of TCP?
5. Why use a CNAME instead of just adding a second A record for the same IP?
6. 401 vs 403 — what's the practical difference?
