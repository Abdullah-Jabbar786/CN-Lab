# Simple DNS Resolver using raw UDP socket programming.
# Constructed a DNS query by hand (RFC 1035 message format), sends it to a
# user-specified DNS server on port 53, and manually parses the response
# (Header + Question + Answer sections): no gethostbyname() or dnspython.

import socket
import struct
import random

DNS_PORT = 53
TIMEOUT = 5  # seconds to wait for a response before giving up on it

QTYPE_A = 1 # asking for IPv4 address record
QCLASS_IN = 1  # Internet class

# RCODE values from the DNS header (RFC 1035, section 4.1.1)
RCODES = {
    0: "NOERROR - No error",
    1: "FORMERR - Format error in query",
    2: "SERVFAIL - Server failed to process query",
    3: "NXDOMAIN - Domain does not exist",
    4: "NOTIMP - Query type not implemented",
    5: "REFUSED - Server refused to answer",
}

def encode_domain_name(domain):
    encoded = b""
    for label in domain.strip(".").split("."):
        if len(label) == 0 or len(label) > 63:
            raise ValueError(f"Invalid label in domain name: '{label}'")
        encoded += struct.pack("B", len(label)) + label.encode("ascii")
    encoded += b"\x00" # terminates the name
    return encoded


def build_dns_query(domain, qtype=QTYPE_A):
    transaction_id = random.randint(0, 65535)
    flags = 0x0100
    qdcount, ancount, nscount, arcount = 1, 0, 0, 0

    header = struct.pack(">HHHHHH", transaction_id, flags,
                          qdcount, ancount, nscount, arcount)
    
    qname = encode_domain_name(domain)
    question = qname + struct.pack(">HH", qtype, QCLASS_IN)
    return header + question, transaction_id


def parse_domain_name(data, offset):
    labels = []
    jumped = False
    offset_after_first_pointer = None

    while True:
        length_byte = data[offset]

        if length_byte == 0:
            offset += 1
            break
        if (length_byte & 0xC0) == 0xC0:  # top two bits set = compression pointer
            if not jumped:
                offset_after_first_pointer = offset + 2
            pointer = struct.unpack(">H", data[offset:offset + 2])[0]
            offset = pointer & 0x3FFF  # low 14 bits hold the target offset
            jumped = True
            continue

        offset += 1
        labels.append(data[offset:offset + length_byte].decode("ascii", errors="replace"))
        offset += length_byte

    final_offset = offset_after_first_pointer if jumped else offset
    return ".".join(labels), final_offset


def parse_dns_response(data, expected_id):

    if len(data) < 12:
        raise ValueError("Response too short to be a valid DNS message")

    transaction_id, flags, qdcount, ancount, nscount, arcount = struct.unpack(">HHHHHH", data[:12])
    if transaction_id != expected_id:
        raise ValueError("Transaction ID mismatch (unexpected/stray reply)")

    rcode = flags & 0xF
    result = {
        "transaction_id": transaction_id,
        "authoritative": bool((flags >> 10) & 0x1),
        "truncated": bool((flags >> 9) & 0x1),
        "recursion_desired": bool((flags >> 8) & 0x1),
        "recursion_available": bool((flags >> 7) & 0x1),
        "rcode": rcode,
        "rcode_text": RCODES.get(rcode, f"Unknown ({rcode})"),
        "ancount": ancount,
        "question": None,
        "answers": [],
    }

    offset = 12

    # Question
    qname, offset = parse_domain_name(data, offset)
    qtype, qclass = struct.unpack(">HH", data[offset:offset + 4])
    offset += 4
    result["question"] = {"name": qname, "qtype": qtype, "qclass": qclass}

    # Answer
    for _ in range(ancount):
        name, offset = parse_domain_name(data, offset)
        rtype, rclass, ttl, rdlength = struct.unpack(">HHIH", data[offset:offset + 10])
        offset += 10
        rdata = data[offset:offset + rdlength]

        record = {"name": name, "type": rtype, "ttl": ttl}
        if rtype == 1 and rdlength == 4:          
            record["address"] = ".".join(str(b) for b in rdata)
        elif rtype == 5:                      
            cname, _ = parse_domain_name(data, offset)
            record["cname"] = cname

        result["answers"].append(record)
        offset += rdlength
    return result

def query_dns_server(domain, server_ip, timeout=TIMEOUT):
    query, transaction_id = build_dns_query(domain)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)

    try:
        sock.sendto(query, (server_ip, DNS_PORT))
        response, _ = sock.recvfrom(512) 
    finally:
        sock.close()
    return parse_dns_response(response, transaction_id)

def is_valid_domain(domain):
    """Reject obviously malformed input before we bother sending a query."""
    if not domain or len(domain) > 253:
        return False
    labels = domain.strip(".").split(".")
    if len(labels) < 2:
        return False
    for label in labels:
        if not label or len(label) > 63 or not all(c.isalnum() or c == "-" for c in label):
            return False
    return True

def print_result(domain, server_ip, result):
    print(f"\n--- DNS Query Result for '{domain}' ---")
    print(f"DNS Server Used   : {server_ip}")
    print(f"Transaction ID    : {result['transaction_id']}")
    print(f"Query Name        : {result['question']['name']}")
    print(f"Query Type        : A ({result['question']['qtype']})")
    print(f"Response Status   : {result['rcode_text']}")
    print(f"Flags             : AA={result['authoritative']} TC={result['truncated']} "
          f"RD={result['recursion_desired']} RA={result['recursion_available']}")
    print(f"Answer Count      : {result['ancount']}")

    if result["rcode"] != 0:
        print("No usable answer — server returned an error status above.")
        return
    if not result["answers"]:
        print("No answer records were returned (empty answer section).")
        return

    for i, ans in enumerate(result["answers"], start=1):
        print(f"\n  Answer {i}:")
        print(f"    Name : {ans['name']}")
        print(f"    TTL  : {ans['ttl']} seconds")
        if "address" in ans:
            print(f"    IPv4 Address : {ans['address']}")
        elif "cname" in ans:
            print(f"CNAME points to : {ans['cname']}")
        else:
            print(f"(Record type {ans['type']}, unhandled RDATA)")

def main():
    print("=== Simple DNS Resolver (raw UDP socket programming) ===")
    server_ip = input("Enter DNS server IP to query (e.g., 8.8.8.8): ").strip()

    while True:
        domain = input("\nEnter a domain name to resolve (or 'quit' to exit): ").strip()

        if domain.lower() in ("quit", "exit", "q"):
            print("Exiting. Goodbye!")
            break
        if not is_valid_domain(domain):
            print("Invalid domain name format. Please try again.")
            continue
        try:
            result = query_dns_server(domain, server_ip)
            print_result(domain, server_ip, result)
        except socket.timeout:
            print(f"Request timed out — no response from {server_ip} within {TIMEOUT}s.")
        except ValueError as e:
            print(f"Error parsing response: {e}")
        except OSError as e:
            print(f"Network error: {e}")

if __name__ == "__main__":
    main()