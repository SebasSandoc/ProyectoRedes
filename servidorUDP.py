import socket

HOST = "127.0.0.1"
PORT = 65433

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind((HOST,PORT))
    print('Servidor UDP esperando')
    while True:
        data, addr = s.recvfrom(1024)
        print(f'recibido de {addr}: {data.decode()}')
        s.sendto(data,addr)


