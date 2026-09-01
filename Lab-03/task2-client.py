import socket

s = socket.socket()
s.connect(('localhost', 9999))
gp = input("Enter your grade point: ")
s.send(gp.encode())

result = s.recv(1024).decode()
print(result)
s.close()