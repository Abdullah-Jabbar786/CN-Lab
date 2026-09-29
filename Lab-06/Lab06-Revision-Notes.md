# CN Lab 6 — Revision Notes: Telnet & SSH

## 1. The core problem both protocols solve

Every prior lab had you sit physically at a device (or its Packet Tracer equivalent) to configure it. Real networks have switches/routers in wiring closets, data centers, or other buildings, nobody walks over with a keyboard every time a config change is needed. **Telnet and SSH both solve "how do I get a command-line session on a remote device over the network instead of standing in front of it."** The difference between them is entirely about *security*, not capability.

## 2. Telnet

**What it is:** a terminal emulation protocol — it runs on your PC, connects to a remote device, and anything you type is executed exactly as if you were on that device's own console.

**The critical weakness:** Telnet sends everything, including the login password, in **plaintext**. Anyone capturing traffic on the path (same concept as the Wireshark plaintext-login exercise from Lab 5) can read your credentials directly. This is precisely why Telnet is considered obsolete for anything security-sensitive today, but it's still taught because it's simple and shows the underlying remote-access concept clearly.

**Key requirement:** each Telnet/SSH/FTP session needs one **vty line** (virtual terminal line) on the device being accessed. `line vty 0 15` configures 16 simultaneous virtual terminal sessions (0 through 15).

### Telnet configuration sequence (on the switch/router being accessed)
```
enable
config t
interface vlan 1
ip address 192.168.1.1 255.255.255.0
no shutdown
exit
line vty 0 15
password cisco
login
exit
enable password cs
```
- `interface vlan 1` + IP — gives the switch itself a management IP address (switches are Layer 2, but still need *an* IP for someone to Telnet/SSH *into the switch itself* for management).
- `line vty 0 15` + `password` + `login` — sets the password required just to get in.
- `enable password` — a **separate** password required to escalate into privileged (enable) mode *after* you're already logged in. Two separate gates: one to log in at all, one to get full control.

**Common failure encountered in this lab, worth remembering:** trying to Telnet before any authentication is configured gets you `[Connection to X.X.X.X closed by foreign host]` — Cisco devices refuse Telnet access entirely until a vty password is set. This isn't a bug, it's a safeguard against leaving a completely open remote-access door.

## 3. SSH (Secure Shell)

**What it is:** the secure replacement for Telnet. It's an **Application layer** protocol (Layer 7) but its defining feature is that it **encrypts** the entire session, login credentials included.

**Two authentication modes:**
- **Password-based:** username + password, same idea as Telnet but encrypted in transit.
- **Key-based:** a cryptographic key pair (public/private) authenticates the client instead of a password — more secure, no password to intercept or guess at all.

### SSH configuration sequence
```
config t
hostname lab01
ip domain name fast-cn
crypto key generate rsa
   (choose modulus size, e.g. 1024)
ip ssh version 2
line vty 0 15
transport input ssh
```
- **`hostname`** — SSH keys are generated using the device's hostname + domain name combined, so the device needs a real hostname first, not the generic "Router"/"Switch" default.
- **`ip domain name`** — paired with hostname to form the full identity used in key generation.
- **`crypto key generate rsa`** — this is the actual cryptographic step: generates the public/private key pair used to encrypt the session. A larger modulus (bit size) is more secure but takes longer to generate.
- **`ip ssh version 2`** — forces the modern, more secure SSH version (version 1 has known vulnerabilities).
- **`transport input ssh`** — this is the important restriction: it tells the vty lines to accept **only SSH**, not Telnet. Without this, both would still work, defeating the point of switching to SSH.

**Changing the default username:**
```
username CS-FAST secret abc
line vty 0 15
login local
```
- `secret` (not `password`) — encrypts the stored password using a hash, unlike the plain `password` keyword used for Telnet/enable, which stores it in plaintext in the config.
- `login local` — tells the vty lines to authenticate against the **local username database** (the `username` command) instead of a single shared vty password.

**Connecting via SSH from a PC:**
```
ssh -l admin 192.168.1.1
ssh -l CS-FAST 192.168.1.1
```
`-l` specifies which username to log in as.

## 4. Telnet vs SSH — the one-line summary

| | Telnet | SSH |
|---|---|---|
| Encryption | None (plaintext) | Full session encryption |
| Auth methods | Password only | Password or key-pair |
| Port | 23 | 22 |
| Use today | Legacy/lab use only | Industry standard |

## 5. Task Topology Notes (this lab's two exercises)

**Lab Exercise I:** 4 switches connected together (Switch0–3), each with 2 end devices. IP scheme: `XX.XX.YY.0` built from your roll number (e.g. roll 3879 → `38.79.1.0`), incrementing the last-but-one segment (Y) for each additional network. Includes verifying Telnet from the nearest switch to each PC, and reconfiguring a switch's IP remotely via Telnet from a *different* PC than the one directly attached to it.

**Lab Exercise II:** 1 router connecting two switch-based sub-networks (6 devices each side). Network addressing: one side uses your roll number directly (e.g. `38.79.1.0`), the other side uses roll number **+1** (e.g. `38.80.2.0`). Router interfaces configured via CLI, one per side, each acting as that side's gateway. Includes `show running-config` on both switches, and using SSH (initiated from a specific laptop) to remotely configure a router interface, mirroring the manual's demonstration of configuring a *second* interface only after SSH access to the *first* is already working.

## High-Yield Viva Questions
1. Why does Telnet let anyone on the network path read your password, but SSH doesn't?
2. Why must a device have a hostname and domain name configured *before* SSH keys can be generated?
3. What's the practical difference between the `password` and `secret` keywords in Cisco IOS?
4. What does `transport input ssh` actually restrict, and what would happen without it?
5. Why does each Telnet/SSH session require its own vty line, and what does `line vty 0 15` actually provide?
