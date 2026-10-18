# DNS Resolver (Raw UDP Sockets)

A DNS query program built with Python sockets. It constructs the DNS query by hand (RFC 1035), sends it over UDP to port 53, and parses the raw response manually. No `gethostbyname()` or DNS libraries are used.

## Features
- Builds the DNS header and question section from scratch
- Sends queries to any DNS server IP provided at runtime
- Parses the header, question, and answer sections, including name compression
- Displays Transaction ID, query name/type, flags, RCODE, A records, and TTL
- Handles invalid domains, NXDOMAIN, timeouts, and malformed responses
- Supports multiple lookups in one run

## How to Run
```bash
python3 dns_resolver.py
```
1. Enter a DNS server IP (e.g. `8.8.8.8`)
2. Enter a domain name (e.g. `www.google.com`)
3. Type `quit` to exit

## Tested With
- `www.google.com` (.com)
- `wikipedia.org` (.org)
- `www.fast.edu.pk` (.edu)

## Requirements
Python 3, standard library only (`socket`, `struct`, `random`).
