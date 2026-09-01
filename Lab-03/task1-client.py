import socket

client_socket = socket.socket()
client_socket.connect(('localhost', 9999))

num1 = input("Enter first number: ")
operation = input("Enter operation (+, -, *, /): ")
num2 = input("Enter second number: ")

message = f"{num1},{operation},{num2}"
client_socket.send(message.encode())

result = client_socket.recv(1024).decode()
print(f"Result: {result}")
client_socket.close()