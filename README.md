# CN-Lab — Computer Networks Lab (CL3001)

A collection of weekly lab manuals and completed solutions for the Computer Networks Lab (CL3001) at FAST-NUCES Karachi.

- Institution: FAST-NUCES Karachi  
- Course: Computer Networks Lab (CL3001)  
- Credit hours: 1  
- Course coordinator: Dr. Farrukh Salim  
- Semester: Fall 2026

See [CLO](./CL3001 - CN Lab - Course Description.pdf) for course learning outcomes and week-by-week topics.

## Contents
- [Structure](#structure)
- [Prerequisites](#prerequisites)
- [How to use this repo](#how-to-use-this-repo)
- [Labs](#labs)
- [Folder & file conventions](#folder--file-conventions)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Structure
Each week's lab folder contains:
- The lab manual/task sheet (PDF or .md)
- My solution: write-up, screenshots, config files, and simulation files

## Prerequisites
May include:
- Cisco Packet Tracer
- Wireshark
- Python 3.x
- Mininet and an OpenFlow controller (e.g., POX, Ryu)
- NS-3
- A terminal with sudo privileges for Mininet

## How to use this repo
1. Clone: git clone <repo-url>  
2. Open the lab folder (e.g., `Lab-01`).  
3. Read the lab manual, then open `solution.md`, `report.pdf`, or the folder README.  
4. For runnable files:
   - Packet Tracer: open `.pkt`
   - Mininet: run the provided `.py` topology (check controller)
   - NS-3: follow the lab README

## Labs

| Week | Folder | Topic |
|---:|---|---|
| 1 | [Lab-01](./Lab-01) | Network basics, topologies, RJ45/cabling, OSI model, classful IP addressing |
| 2 | [Lab-02](./Lab-02) | Cisco Packet Tracer basics, DHCP |
| 3 | [Lab-03](./Lab-03) | Socket programming fundamentals |
| 4 | [Lab-04](./Lab-04) | Wireshark — HTTP/HTTPS/DNS |
| 5 | [Lab-05](./Lab-05) | Application layer protocols (FTP, SMTP) + Wireshark |
| 6 | [Lab-06](./Lab-06) | NS-3 discrete-event simulator |
| 7 | [Lab-07](./Lab-07) | Telnet, SSH, Access Control Lists (ACL) |
| 8 | [Lab-08](./Lab-08) | NAT, intro to SDN with Mininet |
| 9 | [Lab-09](./Lab-09) | Mininet — OpenFlow API |
| 10 | [Lab-10](./Lab-10) | Subnetting and VLSM |
| 11 | [Lab-11](./Lab-11) | Dynamic routing (RIP, OSPF, BGP) |
| 12 | [Lab-12](./Lab-12) | VLANs, cloud networking, IoT overview |

*(More folders will be added as the semester progresses.)*

## Folder & file conventions
- Lab folders: `Lab-01`, `Lab-02`, ...
- Solution file: `solution.md` or `report.pdf`
- Configs: `*.cfg` or `configs/`
- Packet Tracer: `*.pkt`
- Mininet scripts: `*.py`
- Wireshark captures: `*.pcap` / `*.pcapng`

## Contributing
This is a personal lab log. To suggest improvements, open an issue.

## License
Provided under the MIT License. See [LICENSE](./LICENSE).

## Contact
Course coordinator: Dr. Farrukh Salim  
Repository owner: Abdullah-Jabbar786  
Email: k240859@nu.edu.pk
