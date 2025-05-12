import socket

SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

mensaje="hola server"
sock.sendto(mensaje.encode(), (SERVER_IP,SERVER_PORT))

print(f"mensaje enviado a {SERVER_PORT}{SERVER_PORT}")