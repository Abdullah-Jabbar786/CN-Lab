# Simple Client Server Connecting Program

import socket

# Create a socket object
client_socket = socket.socket()

# Connect to the server
client_socket.connect(('localhost', 9999))

# Receive a message from the server
message = client_socket.recv(1024).decode('utf-8')
print(f"Received message: {message}")

# Close the connection
client_socket.close()