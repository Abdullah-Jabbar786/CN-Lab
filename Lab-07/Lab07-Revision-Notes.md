# CN Lab 7: Revision Notes: ACLs & Wireshark (UDP)

## 1. The core problem ACLs solve

Until now, if two networks were connected and routing worked, everyone could talk to everyone. Real networks need rules: "guests can't touch the finance server", "only the admin PC may reach the patient records". **An ACL (Access Control List) is an ordered list of permit/deny rules that a router checks against every packet crossing an interface.** Same hardware, same routes, but now you decide who gets through.

## 2. How an ACL works (the rules that decide everything)

- **Top-down, first match wins.** The router reads rules in order and stops at the first one that matches the packet. Later lines are never checked.
- **Implicit deny at the end.** Every ACL has an invisible `deny ip any any` as its last line. If a packet matches nothing, it dies. That's why you almost always finish with `permit ip any any`.
- **Direction matters.** Applied **inbound** (checked as packets enter the interface) or **outbound** (checked as packets leave). One ACL per interface, per direction.
- **ACLs filter traffic passing *through* the router.** Two PCs on the same switch and subnet never touch the router, so a router ACL can't block them.

### Types

| | Standard | Extended |
|---|---|---|
| Number range | 1 to 99 | 100 to 199 |
| Matches on | Source IP only | Source, destination, protocol, ports |
| Placement | Near the **destination** | Near the **source** |
| Used in this lab | No | Yes, all of it |

**Why extended goes near the source:** it can be precise, so you drop unwanted traffic early instead of dragging it across the network first. Standard ACLs can only see the source, so placing them near the source would block that host from *everything*.

**Numbered vs named:** named (`ip access-list extended NAME`) is easier to read and lets you delete a single line by sequence number. We used named ACLs throughout.

### Wildcard masks

The inverse of a subnet mask. `0` = "must match", `1` = "don't care".

| Want to match | Write |
|---|---|
| One host | `host 8.59.1.2` (same as `8.59.1.2 0.0.0.0`) |
| Whole /24 network | `8.59.1.0 0.0.0.255` |
| Anything | `any` |

## 3. Static routing (needed before any ACL works)

A router only knows networks it is **directly connected** to. For two LANs behind two routers to talk, **each router needs a route to the other side's LAN**. Ping needs a route in both directions, otherwise the request arrives but the reply is dropped.

```
ip route <remote network> <mask> <next-hop IP>
```

## 4. The echo trick (block one direction)

ICMP ping has two message types: **echo** (request) and **echo-reply**.

- To make "A can't reach B, but B can reach A": deny only `echo` from A to B.
- When B pings A, the request passes, and A's reply is *echo-reply*, which the ACL doesn't match, so it passes.
- If you used `deny ip` instead, replies would die too and B couldn't ping A either.

**Rule of thumb:** `deny icmp ... echo` = one-way block. `deny ip ...` = full two-way block.

## 5. Configuration template

```
conf t
ip access-list extended NAME
 permit/deny ip host <src> <dst network> <wildcard>
 ...
 permit ip any any
exit
interface <LAN-facing port>
ip access-group NAME in
end
show ip access-lists
```

**Cleanup between bullets** (each bullet is its own scenario):
```
conf t
interface <port>
no ip access-group NAME in
exit
no ip access-list extended NAME
end
```

**Fix one line without rebuilding:** `ip access-list extended NAME`, then `no 20`, then type the replacement.

### Useful show commands
- `show ip access-lists`: rules plus **match counters** (proof your ACL fired)
- `show ip interface <port>`: which ACL is applied and in which direction
- `show ip route`: confirm the `S` static route and `C` connected lines
- `show ip interface brief`: IPs and `up/up` status
- `show cdp neighbors`: which port connects to which device

## 6. Exercise I: topology and plan

Layout after adding the extra router: `Left LAN - Router0 - Router1 - Right LAN`

| Segment | Network | Router address |
|---|---|---|
| Left | `8.59.1.0/24` | Router0 `Gi0/0` = `.1` |
| Router link | `192.168.1.0/24` | Router0 `Gi0/1` = `.1`, Router1 `Gi0/0` = `.2` |
| Right | `8.60.2.0/24` | Router1 `Gi0/1` = `.1` |

- Router link uses a **crossover** cable. Router-to-switch uses straight-through.
- Static routes: Router0 to `8.60.2.0` via `192.168.1.2`. Router1 to `8.59.1.0` via `192.168.1.1`.
- ACLs sit **inbound on the LAN-facing port** of the router nearest the source.

### The 4 ACL tasks

| Task | Where | Rule logic |
|---|---|---|
| Left can't reach Right, Right can reach Left | Router0 `Gi0/0` in | `deny icmp <left> <right> echo`, `permit ip any any` |
| Only THREE left PCs reach Right | Router0 `Gi0/0` in | 3x `permit ip host`, `deny ip <left> <right>`, `permit ip any any` |
| Block two specific left PCs | Router0 `Gi0/0` in | 2x `deny ip host`, `permit ip any any` |
| Only TWO right PCs reach Left | Router1 `Gi0/1` in | 2x `permit ip host`, `deny ip <right> <left>`, `permit ip any any` |

**Note on the "block two PCs in the left network" wording:** it's ambiguous. A router can't block two PCs on the same subnet from each other, so the practical reading is that those two PCs can't reach the right network.

**Side effect to remember:** with `permit/deny ip` ACLs, blocked devices are cut off **both ways**, because the replies are denied too.

## 7. Exercise II: Hospital Administration vs Patient

Two ISR4331 routers, each with a 5-device switch behind it.

| Segment | Network | Router address |
|---|---|---|
| Hospital Admin | `10.10.1.0/24` | Admin router `Gi0/0/0` = `.1` |
| Router link | `192.168.10.0/24` | Admin `Gi0/0/1` = `.1`, Patient `Gi0/0/0` = `.2` |
| Patient | `10.10.2.0/24` | Patient router `Gi0/0/1` = `.1` |

- ISR4331 ports are named `Gi0/0/0`, `Gi0/0/1`, `Gi0/0/2` (three numbers, not two).
- Admin devices `10.10.1.2` to `.6`, Patient devices `10.10.2.2` to `.6`.

### The 6 ACL bullets

| # | Requirement | Router and port | Rule logic |
|---|---|---|---|
| 1 | Patient can't reach Admin, Admin can reach Patient | Patient router `Gi0/0/1` in | `deny icmp <patient> <admin> echo` + permit any |
| 2 | Only THREE Patient PCs reach Admin | Patient router `Gi0/0/1` in | 3x permit host, deny network, permit any |
| 3 | Admin can't reach Patient, Patient can reach Admin | Admin router `Gi0/0/0` in | `deny icmp <admin> <patient> echo` + permit any |
| 4 | Only TWO Admin PCs reach Patient | Admin router `Gi0/0/0` in | 2x permit host, deny network, permit any |
| 5 | Block ONE Patient PC from all of Admin | Patient router `Gi0/0/1` in | `deny ip host <pc> <admin>` + permit any |
| 6 | Patient can reach Admin, Admin can't reach ONE Patient PC | Admin router `Gi0/0/0` in | `deny icmp <admin> host <pc> echo` + permit any |

## 8. Mistakes I hit (and how to spot them)

1. **`deny ip any any` instead of `permit`** as the last line. Everything else got blocked, including replies. The counters showed the deny line matching 11 times. Always check the last line says `permit`.
2. **The `deny` line silently missing** from a "only N allowed" ACL. The ACL looked fine but blocked nothing, because blocked hosts fell through to `permit ip any any`. Count the lines in `show ip access-lists` before testing.
3. **Typos get rejected** (`permit ip any nay` gives `% Invalid input`). The bad line just doesn't enter, so re-read the output after pasting.
4. **Router port assumed wrong.** ISR4331 cable ports weren't where I guessed. `show cdp neighbors` shows which local port faces which device.
5. **Interface left `unassigned`.** The ping failed silently until `show ip interface brief` showed the missing IP. Router config lines had never been applied.
6. **Missing return route.** Request arrives, reply has nowhere to go, ping times out. Check `S` lines in `show ip route` on both routers.
7. **First ping loses 1 to 2 packets.** That's ARP resolving, not a fault. Run it twice.
8. **`Request timed out` vs `Destination host unreachable`.** Timeout means the packet died silently (routing or config fault). "Unreachable" from the router's own IP means an ACL or missing route rejected it.

### Debug ladder (ping outward one hop at a time)
Own gateway, then the near router's link IP, then the far router's link IP, then the far router's LAN IP, then the target PC. **The first ping that fails is where the problem is.**

## 9. Wireshark: UDP exercise (packet #15)

Open `WiresharkLab5H.pcapng`, filter `udp`, click packet **No. 15** (a DNS query). Answers come from the middle details pane.

| Q | Where to look | Answer |
|---|---|---|
| Domain queried | Domain Name System > Queries > Name | `gaia.cs.umass.edu` |
| Ports | User Datagram Protocol > Source/Destination Port | Source `58350`, destination `53` |
| IPs | Internet Protocol Version 4 > Source/Destination Address | Source `10.0.0.44`, destination `75.75.75.75` |
| UDP header fields | Count real fields under UDP | **4**: source port, destination port, length, checksum (2 bytes each, 8 total) |
| Max UDP payload | Length field is 16 bits | **65,507 bytes** |

**Max payload working:**
- The Length field is 16 bits, so the max is 65,535 bytes.
- That includes the 8-byte UDP header: 65,535 - 8 = 65,527.
- UDP sits in an IPv4 packet capped at 65,535 as well, so subtract the 20-byte IP header too: 65,535 - 20 - 8 = **65,507**.

**Extras worth knowing:**
- Port **53** = DNS. The destination port tells you the service, and the source port is a random ephemeral one.
- Packet #15's UDP length is 43 bytes: 8 header + 35 of DNS query.
- `10.0.0.44` is a private address (a LAN host). `75.75.75.75` is the DNS server it asked.
- The reply (#17) swaps source and destination, both IPs and ports.
- Wireshark's bracketed lines like `[Checksum Status]` are computed by Wireshark, not real header fields.

## High-Yield Viva Questions
1. Why does an ACL end with an implicit deny, and why do we add `permit ip any any`?
2. Why are extended ACLs placed near the source and standard ones near the destination?
3. How can you block A from reaching B while still letting B reach A? Why does `deny icmp ... echo` do it but `deny ip` doesn't?
4. What does the wildcard mask `0.0.0.255` match, and what does `host 8.59.1.2` mean?
5. Why do both routers need a static route for a ping between their LANs to work?
6. What's the difference between inbound and outbound ACL application, and which did we use?
7. What does "Request timed out" tell you compared to "Destination host unreachable"?
8. How many fields are in a UDP header, and why can a UDP payload never be a full 65,535 bytes?
