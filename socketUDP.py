import socket

HOST = "0.0.0.0"
PORT = 12345

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST,PORT))

print(f"sevidor UDP  escuchando en {HOST}:{PORT}")

while True:
    data, addr = sock.recvfrom(1024)
    print(f"Mensaje recibido de {addr}: {data.decode()}")
