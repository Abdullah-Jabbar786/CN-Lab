# CN Lab 1 — Revision Notes

## 1. Core Theory

**Network purpose:** lets multiple hosts exchange data without manual transfer.
**Host** = end device that originates/consumes data (PC, server). **Intermediate devices** (hub, switch, router) forward traffic but aren't hosts.

**Scope classification:**
| Type | Scope |
|---|---|
| LAN | One building/campus, you own the wiring |
| MAN | City-wide, shared metro infrastructure |
| WAN | Country/global, many owners, internet-scale routing |

**Topologies — trade-off is always cost vs fault tolerance vs manageability:**
- **Bus**: one shared cable, cheapest, but one break kills everyone on that segment.
- **Ring**: each host linked to 2 neighbors in a loop.
- **Star**: every host → one central switch/hub. Dominant real-world design — a broken cable only kills that one host, easy to manage/expand.
- **Mesh**: every host ↔ every host. Best fault tolerance, but cost scales as $\frac{n(n-1)}{2}$ — impractical beyond a handful of nodes.
- **Tree**: hierarchical stars — how real buildings/campuses are wired.

## 2. RJ45 & Cabling

- **RJ45**: standardized 8-pin connector for twisted-pair Ethernet cable.
- **T568A / T568B**: two equally valid wiring color-order standards — pick one and stay consistent.
- **Straight-through cable**: same standard both ends → connects **different device types** (PC–switch, router–modem). Needed because switches/hubs internally swap TX/RX for you.
- **Crossover cable**: T568A one end + T568B other → connects **same device types** (PC–PC, switch–switch, router LAN port–switch normal port). The cable itself does the TX/RX swap since neither end-device does it internally.
- **Auto-MDI/MDI-X**: modern NICs auto-detect and swap as needed, straight vs crossover often doesn't matter anymore in practice.

## 3. Key Terminologies (the delivery chain)

MAC (local delivery) → IP (cross-network delivery) → Port (right app on destination) → DNS (name→IP translation) → DHCP (auto IP assignment) → Gateway (exit door out of your LAN).

| Term | One-liner |
|---|---|
| NIC | Hardware interface to the network |
| MAC | Physical, flat, burned-in address — local delivery only |
| Hub | Dumb repeater, broadcasts to all ports |
| Switch | Learns MAC-to-port mapping, forwards intelligently (Layer 2) |
| Router | Forwards between networks using IP (Layer 3) |
| IP address | Logical, hierarchical (network+host) — enables global routing |
| Port | Identifies the app on a host (0–65535) |
| Gateway | Router IP a host sends outbound traffic to |
| Domain name | Human-friendly name mapped to an IP |
| DNS | Resolves domain name ↔ IP |
| DHCP | Auto-assigns IP/gateway/DNS to a joining host |

## 4. OSI Model (top to bottom: **A**ll **P**eople **S**eem **T**o **N**eed **D**ata **P**rocessing)

| Layer | Job | Key device |
|---|---|---|
| 7 Application | App-level interface | — |
| 6 Presentation | Format/encrypt/compress | — |
| 5 Session | Manage session start/end | — |
| 4 Transport | End-to-end reliability (TCP/UDP) | — |
| 3 Network | Logical addressing/routing (IP) | Router |
| 2 Data Link | Physical addressing/framing (MAC) | Switch |
| 1 Physical | Raw bits over the medium | Hub/cable |

**Key idea:** MAC address gets rewritten hop-by-hop; destination IP stays the same end-to-end.

## 5. Task Commands Cheat Sheet

| Task | Command (Windows) | What it tells you |
|---|---|---|
| Own IP + version | `ipconfig` | IPv4/IPv6 address |
| Subnet mask, MAC, gateway, DHCP | `ipconfig /all` | Full adapter config |
| Hostname | `hostname` | Local machine name (resolution over network needs NetBIOS/DNS) |
| Basic connectivity test | `ping <host>` | ICMP echo request/reply — reachable or not |
| Ports in use by apps | `netstat -ano` | Active TCP/UDP connections + PID |
| Router path + hop count | `tracert <site>` | Hop-by-hop route to destination |
| All hosts on local network | `arp -a` | IP↔MAC mappings your machine has seen |
| TCP-only connections | `netstat -an -p TCP` | Filtered connection list |
| Datagrams sent/received | `netstat -s` | Per-protocol traffic statistics |

**Ping vs traceroute:** ping = yes/no + latency only. traceroute = full hop-by-hop path, tells you *where* a failure/slowdown is happening.

**Name resolves but ping-by-IP works, ping-by-name fails:** network layer is fine; it's a name-resolution failure (NetBIOS/DNS can't map the hostname to an IP).

## 6. Cabling Quick Answers
- Same wiring order both ends → **straight-through**
- Router port → PC NIC → **crossover needed** (No to straight-through)
- Switch → PC/server → **straight-through** (No to crossover)
- Hub → PC/server → **straight-through** (Yes)

## 7. Classful IP Addressing

| First octet | Class | Network portion | Default mask |
|---|---|---|---|
| 0–127 | A | 1st octet | 255.0.0.0 |
| 128–191 | B | first 2 octets | 255.255.0.0 |
| 192–223 | C | first 3 octets | 255.255.255.0 |
| 224–239 | D | — (multicast) | — |
| 240–255 | E | — (experimental) | — |

**Rule:** class is decided by the first octet's number alone, comparing against 127/191/223 — nothing else about the address (trailing zeros, "how it looks") matters.

**Network address** = host bits all zero (represents the network itself, never assigned to a device).
**Host address (isolated notation)** = network bits zeroed, only host ID shown.

**With an explicit subnet mask given:** compare IP and mask octet-by-octet — wherever mask = 255, zero that octet out (network); wherever mask = 0, keep the IP value (host). This overrides the classful default whenever a mask is explicitly provided (this is real-world subnetting).

**Private IP ranges (never routed publicly, used inside LANs — NAT translates to a public IP at the gateway):**
- Class A: 10.0.0.0 – 10.255.255.255
- Class B: 172.16.0.0 – 172.31.255.255
- Class C: 192.168.0.0 – 192.168.255.255

## High-Yield Viva Questions
1. Switch vs router — why can't a switch route between networks? (No IP/routing table logic, MAC-only, Layer 2)
2. Why both MAC and IP? (MAC = flat/local, IP = hierarchical/global, needed for internet-scale routing)
3. What changes hop-by-hop vs end-to-end in a packet's journey? (MAC changes per hop, destination IP stays constant)
4. Why does DHCP matter? (Avoids manual config + IP conflicts at scale)
5. Ping vs traceroute — what does each actually tell you?
