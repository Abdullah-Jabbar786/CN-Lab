import socket
import json
import os

FILENAME = "calculations.json"

def calculate(num1, operation, num2):
    if operation == '+':
        return num1 + num2
    elif operation == '-':
        return num1 - num2
    elif operation == '*':
        return num1 * num2
    elif operation == '/':
        if num2 == 0:
            return "Error: Division by zero"
        return num1 / num2
    else:
        return "Error: Invalid operation"

def save_to_file(num1, operation, num2, result):
    # Load existing records if the file already exists
    if os.path.exists(FILENAME):
        with open(FILENAME, 'r') as f:
            records = json.load(f)
    else:
        records = []

    # Add the new record
    records.append({
        "num1": num1,
        "operation": operation,
        "num2": num2,
        "result": result
    })

    # Save the whole list back
    with open(FILENAME, 'w') as f:
        json.dump(records, f, indent=4)

server_socket = socket.socket()
server_socket.bind(('localhost', 9999))
server_socket.listen(5)
print("Server is listening, waiting for a connection...")

while True:
    client_socket, addr = server_socket.accept()
    print(f"Got connection from {addr}")

    data = client_socket.recv(1024).decode()
    print(f"Received: {data}")

    num1, operation, num2 = data.split(',')
    num1 = float(num1)
    num2 = float(num2)

    result = calculate(num1, operation, num2)
    save_to_file(num1, operation, num2, result)

    client_socket.send(str(result).encode())
    client_socket.close()