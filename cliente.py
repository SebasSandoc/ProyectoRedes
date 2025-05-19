import socket
import threading

HOST = "127.0.0.1"
PORT_TCP = 12345
PORT_UDP = 12346

def cliente_tcp():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST,PORT_TCP))

    def recibir():
        while True:
            try:
                msg = sock.recv(1024).decode()
                if msg:
                    print(msg)
            except:
                break
    
    threading.Thread(target=recibir, daemon=True).start()

    while True:
        try:
            msg = input()
            if msg.upper() == "SALIR":
                sock.send(b"SALIR")
                print("Desconectado del chat")
                sock.close()
                break
            sock.send(msg.encode())
        except:
            break

def cliente_udp():
    servidor_addr = (HOST,PORT_UDP)
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0",0))

    def escuchar():
        while True:
            try:
                msg, _ = sock.recvfrom(1024)
                print(msg.decode())
            except:
                break
    threading.Thread(target=escuchar, daemon=True).start()
    print("===Chat UDP===")
    nombre = input("Ingresa tu nombre de usuario nombre de usuario: ")
    try:
        while True:
            msg = input()

            if msg.upper() == "SALIR":
                salir_msg = f"{nombre}::SALIR"
                sock.sendto(salir_msg.encode(), servidor_addr)
                print("Desconectado chat UDP")
                sock.close()
                break
            texto = f"{nombre}: {msg}"
            sock.sendto(texto.encode(),servidor_addr)
    except:
        sock.close()

#Menu Protocolo
def menu():
    while True:
        print("Chat TCP y UDP")
        op = input("Selecionar modo\n1. TCP\n2. UDP\nEscribe SALIR para cerrar el programa\n")
        if op == "1":
            cliente_tcp()
        elif op =="2":
            cliente_udp()
        elif op == "SALIR":
            print("Programa cerrado")
            break
        else:
            print("Opcion invalida")

menu()

