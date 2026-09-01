import socket

def get_grade(gp):
    scheme = [
        (4.33, "A+", "Excellent"),
        (4.00, "A",  "Excellent"),
        (3.66, "A-", "Very good"),
        (3.33, "B+", "Very good"),
        (3.00, "B",  "Very good"),
        (2.66, "B-", "Good"),
        (2.33, "C+", "Good"),
        (2.00, "C",  "Good"),
        (1.66, "C-", "Passable"),
        (1.33, "D+", "Passable"),
        (1.00, "D",  "Passable"),
        (0.00, "E",  "Failure"),
    ]
    for point, letter, qualification in scheme:
        if gp >= point:
            return letter, qualification
    return "E", "Failure"

s = socket.socket()
s.bind(('localhost', 9999))
s.listen(5)
print("Server started, waiting for connection...")

while True:
    c, addr = s.accept()
    print("Got connection from", addr)

    data = c.recv(1024).decode()
    gp = float(data)

    letter, qualification = get_grade(gp)
    response = f"Grade Point {gp} -> Letter Grade: {letter}, Qualification: {qualification}"

    c.send(response.encode())
    c.close()