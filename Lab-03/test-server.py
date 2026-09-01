# Simple Client Server Connecting Program

import socket

#create a socket object
server_socket = socket.socket()   
print("Socket successfully created")

#Bind the socket to a public host, and a well-known port
server_socket.bind(('localhost', 9999))

#Listen for connections
server_socket.listen(5)
print("Socket is listening, Waiting for a connection...")

while True:
    client_socket, addr = server_socket.accept()  
    # Establish connection with client.
    print(f"Got connection from {addr}")
    client_socket.send(b'Thank you for connecting')

    client_socket.close()  # Close the connection with the client.