import socket
import threading

HOST = "0.0.0.0"
TCP_PORT = 12345
UDP_PORT = 12346

clientes_tcp = []
clientes_udp = []

def cargar_usuarios():
    usuarios={}
    with open("usuarios.txt","r") as f:
        for linea in f:
            if ":" in linea:
                usuario,clave = linea.strip().split(":")

#clientes TCP autenticado
def manejar_clientes_tcp(conn,addr):
    try:
        conn.sendall("Usuarios: ".encode())
        usuario = conn.recv(1024).decode().strip()

        conn.sendall("Contraseña: ".encode())
        clave = conn.recv(1024).decode().strip()

        if usuarios_validos.get(usuario) != clave:
            conn.sendall("Usuario o contraseña incorrectos.".encode())
            conn.close()
            return
        conn.sendall(f"bienvenido {usuario}".encode())
        print(f"[TCP] {usuario} conectado desde {addr}")
        clientes_tcp.append(conn)

        while True:
            data = conn.recv(1024)
            if not data:
                break
            mensaje = f"[TCP] {usuario}: {data.decode()}"
            print(mensaje)
            for c in clientes_tcp:
                if c != conn:
                    try:
                        c.sendall(mensaje.encode())
                    except:
                        pass
    finally:
        if conn in clientes_tcp:


#Clientes UDP
def recibir_udp():
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind((HOST, UDP_PORT))
    print(f"Servidor UDP escuchando en puerto {UDP_PORT}")

    while True:
        data, addr = udp_sock.recvfrom(1024)
        mensaje = f"[UDP] {addr}:{data.decode()}"
        print(mensaje)
        for c in clientes_udp:
            if c != addr:
                udp_sock.sendto(mensaje.encode(),c)
        if addr not in clientes_udp:
            clientes_udp.append(addr)

#servidor TCP
def iniciar_tcp():
    tcp_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    tcp_sock.bind(HOST,TCP_PORT)
    tcp_sock.listen()
    print(f"servidor tcp escuchando en puerto {TCP_PORT}")

    while True:
        conn, addr = tcp_sock.accept()
        threading.Thread(target=manejar_clientes_tcp, args=(conn,addr),
daemon=True).start()
    
#IP local

def obtener_ip_local():
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.connect(("8.8.8.8",80))
    ip = s.getsockname()[0]
    s.close
    return ip

print(f"IP del servidor: {obtener_ip_local()}")
threading.Thread(target=iniciar_tcp, daemon=True).start()   
threading.Thread(target=iniciar_udp, daemon=True).start()

input("sevidor activo. presiona enter para salir... ")