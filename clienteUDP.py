import socket

HOST = "127.0.0.1"
PORT = 65433

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.sendto(b'conexion con servidor UDP',(HOST,PORT))
    data,_ = s.recvfrom(1024)

print('respuesta del servidor:',data.decode())