import socket
import threading
from datetime import datetime

usuarios_en_linea = {}
UDP_clientes = set()
UDP_nombres = {}
UDP_direcciones = {}
HOST = "127.0.0.1"
PORT_TCP = 12345
PORT_UDP = 12346

#Funcion para obtener la hora y fecha
def obtener_tiempo():
    return datetime.now().strftime("[%H:%M:%S | %d-%m-%Y]")

#Obtener los usuarios registrados
def cargar_usuarios():
    try:
        with open("usuarios.txt","r") as f:
            return dict(line.strip().split(":")for line in f)
    except FileNotFoundError:
        return {}

#Registra usuarios para TCP    
def registrar_usuario(username, password):
    with open("usuarios.txt","a") as f:
        f.write(f"{username}:{password}\n")

usuarios_registrados = cargar_usuarios()

#Manejar clientes con TCP

def manejar_clientes_tcp(cliente,direccion):
    cliente.send(b"===Chat Servidor TCP===\n1.LOGIN\n2.REGISTRO\n")
    op = cliente.recv(1024).decode().strip().upper()

    cliente.send(b"Usuario: ")
    usuario = cliente.recv(1024).decode().strip()
    cliente.send(b"Contrasenia: ")
    password = cliente.recv(1024).decode().strip()

    if op == "2":
        if usuario in usuarios_registrados:
            cliente.send(b"El usuario ya existe. Conecion cerrada")
            cliente.close()
            return
        usuarios_registrados[usuario] = password
        registrar_usuario(usuario,password)
        cliente.send(b"Su usuario ha sido registrado")
    elif op == "1":
        if usuarios_registrados.get(usuario) != password:
            cliente.send(b"Usuario o contrasenia incorrectos. Conexion cerrada")
            cliente.close()
            return
        cliente.send(b"login exitoso")
    else:
        cliente.send(b"opcion invalida. Conexion cerrada")
        cliente.close()
        return

    usuarios_en_linea[usuario] = cliente
    trasmitir_tcp(f"[{usuario} se ha conectado]", cliente)

    try:
        while True:
            msg = cliente.recv(1024).decode()
            if not msg:
                break
            
            #Mensaje privado TCP
            if msg.startswith("@"):
                try:
                    objetivo, texto_privado = msg[1:].split(":", 1)
                    objetivo = objetivo.strip()
                    texto_privado = texto_privado.strip()

                    if objetivo in usuarios_en_linea:
                        objetivo_socket = usuarios_en_linea[objetivo]
                        marca = obtener_tiempo()
                        mensaje_privado = f"{marca} [Privado de {usuario}]: {texto_privado}"
                        objetivo_socket.send(mensaje_privado.encode())
                        cliente.send(f"{marca} [Privado a {objetivo}]: {texto_privado}".encode())
                    else:
                        cliente.send(f"Usuario '{objetivo}' no encontrado.".encode())
                except:
                    cliente.send(b"Formato invalido. Usa: @usuario: mensaje")
                continue           

            if msg.strip().upper() == "SALIR":
                print(f"[{usuario} ha salido del chat TCP]")
                break

            marca = obtener_tiempo()
            print(f"{obtener_tiempo()} [TCP] mensaje de {usuario}:{msg}")          
            trasmitir_tcp(f"{marca} [{usuario}]: {msg}",cliente)
    finally:
        cliente.close()
        if usuario in usuarios_en_linea:
            del usuarios_en_linea[usuario]
            trasmitir_tcp(f"[{usuario} se ha desconectado]",None)

#Transmitir a traves de TCP
def trasmitir_tcp(mensaje,remitente):
    for sock in usuarios_en_linea.values():
        if sock != remitente:
            try:
                sock.send(mensaje.encode())
            except:
                pass

#Manejar socket UDP
def manejar_udp(udp_socket):
    print("Servidor UDP esperando en el puerto 12346")
    while True:
        try:
            data, addr = udp_socket.recvfrom(1024)          
            
            mensaje = data.decode().strip()
            marca = obtener_tiempo()
            if ":" in mensaje:
                partes = mensaje.split(":", 1)
                remitente = partes[0].strip()
                contenido = partes[1].strip()
            else:
                remitente = "Desconocido"
                contenido = mensaje
            mensaje_formato = f"{marca} {mensaje}"

            if addr not in UDP_nombres and ":" in mensaje:
                nombre = mensaje.split(":",1)[0]
                UDP_nombres[addr] = nombre
                UDP_direcciones[nombre] = addr
                UDP_clientes.add(addr)

            #Mensaje privado para UDP
            if contenido.startswith("@"):
                try:
                    objetivo, texto_privado = contenido[1:].split(":", 1)
                    objetivo = objetivo.strip()
                    texto_privado = texto_privado.strip()
                    mensaje_privado = f"{marca} [Privado de {remitente}]: {texto_privado}"

                    if objetivo in UDP_direcciones:
                        udp_socket.sendto(mensaje_privado.encode(), UDP_direcciones[objetivo])
                        udp_socket.sendto(f"{marca} [Privado a {objetivo}]: {texto_privado}".encode(), addr)
                    else:
                        udp_socket.sendto(f"Usuario '{objetivo}' no encontrado.".encode(), addr)
                except:
                    udp_socket.sendto("Formato inválido. Usa: @usuario: mensaje".encode(), addr)
                continue

            if mensaje.endswith("::SALIR"):
                nombre =UDP_nombres.get(addr, "Usuario")
                print(f"Cliente UDP {addr} se ha desconectado")
                UDP_clientes.discard(addr)
                UDP_nombres.pop(addr,None)

                mensaje_salida = f"[{nombre} ha salido del chat]"
                for cliente in list(UDP_clientes):
                    try:
                        udp_socket.sendto(mensaje_salida.encode(),cliente)
                    except:
                        UDP_clientes.discard(cliente)
                        UDP_nombres.pop(cliente,None)
                continue           

            #UDP_clientes.add(addr)
            print(f"{obtener_tiempo()} [UDP] {addr}: {data.decode()}")

            for cliente in list(UDP_clientes):
                if cliente != addr:
                    try:
                        udp_socket.sendto(mensaje_formato.encode(), cliente)
                    except Exception as e:
                        print(f"No se pudo enviar a {cliente}: {e}")
                        UDP_clientes.discard(cliente)
                        UDP_nombres.pop(cliente, None)
        except Exception as e:
            print("Error UDP:",e)

def iniciar_server():
    #TCP
    tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_server.bind((HOST,PORT_TCP))
    tcp_server.listen()
    print("Servidor TCP esperando en el puerto 12345")

    threading.Thread(target=aceptar_tcp, args=(tcp_server,),daemon=True).start()

    #UDP
    udp_server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    udp_server.bind((HOST,PORT_UDP))
    manejar_udp(udp_server)

def aceptar_tcp(tcp_server):
    while True:
        cliente, direccion = tcp_server.accept()
        print(f"Conexion tcp aceptada desde {direccion}")
        threading.Thread(target=manejar_clientes_tcp, args=(cliente,direccion)).start()

iniciar_server()


