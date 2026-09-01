print("Hello")


# Importing Socket module: 
import socket
hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)

print("Hostname: " + hostname)
print("IP Address: " + IPAddr)


# Getting any host IP address in python:
hostnames = ["www.google.com", "www.facebook.com", "www.youtube.com"] # List of hostnames to resolve.

for hostname in hostnames:
    try:
        ip_address = socket.gethostbyname(hostname)
        print(f"IP address of {hostname} is {ip_address}")
    except socket.gaierror:
        print(f"Could not resolve hostname: {hostname}")

#Getting hostname by IP address in python:
hname = socket.gethostbyaddr(IPAddr)
hname1 = socket.gethostbyaddr('8.8.8.8')
print(f"Hostname of {IPAddr} is {hname[0]}")
print(f"Hostname of 8.8.8.8 is {hname1[0]}")


# Getting service name, given port number & protocol in python:

def get_service_name():
    protocol_name = 'tcp'
    for port in [80, 25]:
        print("Port %s --> Service Name: %s" % (port, socket.getservbyport(port, protocol_name)))


# PortScanner:

import time

start_time = time.time()
if __name__ == '__main__':
    target = input("Enter the host to be scanned: ")
    target_ip = socket.gethostbyname(target)
    print(f"Starting scan on host: {target_ip}")

    for port in range(50, 500):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket.setdefaulttimeout(1)
        result = sock.connect_ex((target_ip, port))
        if result == 0:
            print(f"Port {port}: Open")
        sock.close()

    end_time = time.time()
    print(f"Scanning completed in {end_time - start_time:.2f} seconds")
