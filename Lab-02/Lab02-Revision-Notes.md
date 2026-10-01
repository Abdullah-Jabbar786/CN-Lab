# CN Lab 2 — Revision Notes: Packet Tracer Basics & DHCP

## 1. What Packet Tracer actually is

A **protocol simulator** (built by Cisco) that visually shows protocols operating across OSI layers, Layer 2 (Ethernet, PPP), Layer 3 (IP, ICMP, ARP), Layer 4 (TCP, UDP), plus routing protocols, in either **Realtime** mode (instant, like a real network) or **Simulation** mode (step-by-step, packet by packet).

## 2. Building a topology — the actual workflow

1. **Choose a device category** (End Devices, Switches, Hubs, etc.) on the bottom-left panel, then click the specific model.
2. **Click in the topology canvas** to place it, the cursor turns into a `+` when ready to drop a device.
3. **Connect devices** via the **Connections** tool, pick a cable type, then click the first device → choose its port → drag to the second device → choose its port.

## 3. Cable type rule (same logic as Lab 1, now applied hands-on)

- **Copper Straight-through** — connects **different device types** (PC to hub, PC to switch).
- **Copper Crossover** — connects **like devices** (hub to switch, switch to switch). This lab explicitly has you crossover-cable a Hub to a Switch, a direct hands-on example of the "same device type" rule from Lab 1.

## 4. Hub vs Switch — visible proof, not just theory

Both get connected the same way, but watch the **port light behavior**:
- A link to a **hub** turns straight to **green** (hubs have no intelligence, nothing to negotiate).
- A link to a **switch** port starts **amber**, then turns **green** after about 30 seconds. That delay is **Spanning Tree Protocol (STP)** running, the switch is temporarily blocking frame forwarding on that port while STP determines the network isn't looping. Only once it reaches the "forwarding" state does traffic actually pass. **This is why newly-connected switch ports sometimes seem "broken" for a short time, it's STP doing its job, not a cabling mistake.**

## 5. Configuring hosts

**Config tab → Settings**: rename the device, set **Gateway IP** (default router address) and **DNS Server IP** here.
**Config tab → Interface → FastEthernet**: assign the actual **IP Address** and **Subnet Mask**.
**Bandwidth/Duplex**: default is **Auto** (auto-negotiation):
- Hub connection → NIC auto-selects **Half Duplex** (hubs are shared-medium, can't have both sides talk at once without collision).
- Switch connection (with the port set to Full Duplex or Auto) → NIC selects **Full Duplex** (switch gives each device a dedicated collision-free link, so both directions can carry traffic simultaneously). Full Duplex is always the more efficient option when available.

## 6. Verifying connectivity

**Add Simple PDU tool** (looks like an envelope) — click source device, then destination device, sends a test ping. **PDU Last Status: Successful** confirms the path works.

**Realtime mode** — connectivity test happens instantly, like real life.
**Simulation mode** — same test, but you step through it packet by packet using **Capture/Forward**, watching the ICMP messages physically move hop by hop through hub/switch/destination. Use **Edit Filters → All/None** to isolate just the protocol you care about (e.g. just ICMP), exactly the same filtering workflow you later reused in Labs 4-6.

## 7. Resetting a simulation

**Delete** (clears the PDU test) → **Power Cycle Devices** (restarts everything) → wait for STP to re-settle (amber → green again on switch ports) before testing again.

## 8. Saving your work

Topologies save as **`.pkt`** files, this is the file format every later lab's "submit a .pkt file" instruction refers to.

## 9. DHCP (Dynamic Host Configuration Protocol)

**Purpose:** automatically distributes IP addresses to devices on a network, so nobody has to type static IPs in by hand (direct contrast to everything you manually configured earlier in this same lab).

**The process, as the manual describes it:**
1. **DHCP DISCOVER** — a device joining the network broadcasts a request for an IP
2. **DHCP OFFER** — the DHCP server responds, offering an available address from its pool
3. **DHCP REQUEST** — the client replies, formally requesting that offered address

**Worth knowing for completeness** (the manual simplifies slightly): the full real-world process has a 4th step, **DHCP ACK**, the server's final acknowledgment confirming the lease. This 4-step sequence is commonly called **DORA** (Discover, Offer, Request, Acknowledge), worth having the complete version in mind for a viva even though this manual only names the first three.

**Setup in Packet Tracer:**
1. Add 3 PCs + 1 Server, connect all to a switch
2. Click the Server → **Fast Ethernet** → assign it a **static** IP (the server itself needs a fixed address, same reasoning as every later lab: infrastructure gets static IPs, clients get dynamic ones)
3. Still on the server, enable the **DHCP** service, this turns the server into an address-dispensing pool
4. On each PC → **Desktop → IP Configuration → select DHCP** (instead of Static), each one then automatically receives an address from the server's pool
