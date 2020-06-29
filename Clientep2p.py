# !/usr/bin/env python3
import socket
import sys
import threading
import random
import os
import shutil
import time
#buffer_size = 1024

'''HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)
buffer_size = 1024'''

def servirPorSiempre(socketTcp, listaConexiones):
    try:
        while True:
            Client_conn, Client_addr = socketTcp.accept()
            #print("Conectado a", Client_addr)
            gestion_conexiones(listaConexiones, Client_conn)
            thread_read = threading.Thread(target=ShareFunction, args=[Client_conn])
            thread_read.start()
    except Exception as e:
        print(e)

def ShareFunction(Client_Conn):
    ArchivosDisponibles(Client_Conn)
    filename = Client_Conn.recv(1024)
    filename = filename.decode('utf-8')
    if os.path.isfile(filename):
        win = "EXISTE " + str(os.path.getsize(filename))
        Client_Conn.send(str.encode(win))
        RespUsuario = Client_Conn.recv(1024)
        RespUsuario = RespUsuario.decode('utf-8')
        if RespUsuario[:2] == 'OK':
            with open(filename, 'rb') as f:
                bytesToSend = f.read(1024)
                Client_Conn.send(bytesToSend)
                while bytesToSend != "":
                    bytesToSend = f.read(1024)
                    Client_Conn.send(bytesToSend)
    else:
        Client_Conn.send(str.encode("ERROR"))

    Client_Conn.close()

def ArchivosDisponibles(Client_Conn):
    Datos = os.listdir(".")
    Datos = str(Datos)
    Client_Conn.send(str.encode(Datos))

def gestion_conexiones(listaconexiones, conn):
    listaconexiones.append(conn)
    for conn in listaconexiones:
        if conn.fileno() == -1:
            listaconexiones.remove(conn)
    #print("conexiones: ", len(listaconexiones))

def modo_Usuario():
    encendido = -1
    while encendido != 0:
        encendido = BuscarFile()

def BuscarFile():
    print("200 OK\n" + "[1] Buscar Archivo\n")
    resp = int(input())
    if resp == 1:
        HOST = "localhost"
        PORT = 65432
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPClientsocket:
            TCPClientsocket.connect((HOST, PORT))
            lista = TCPClientsocket.recv(1024)
            lista = lista.decode('utf-8')
            print("\nArchivos disponibles en la Red\n" + lista)
            opcion = int(input("[1] Aceptar\n[0] Cancelar\n"))
            if(opcion == 1):
                filename = input("Archivo: ")
                filename = str(filename)
                if filename != 'q':
                    TCPClientsocket.send(str.encode(filename))
                    data = TCPClientsocket.recv(1024)
                    data = data.decode('utf-8')

                    if data[:6] == "EXISTE":
                        tamFile = float(data[6:])
                        mensaje = input("Archivo Existente, "+str(tamFile)+\
                            "Bytes, ¿Desea Descargarlo? [Y/N]? -> ")
                        if mensaje == 'Y':
                            TCPClientsocket.send(str.encode("OK"))
                            f = open('new_'+filename ,'w')
                            data = TCPClientsocket.recv(1024)
                            data = data.decode('utf-8')
                            totalRecv = len(data)
                            f.write(data)
                            while totalRecv < tamFile:
                                data = TCPClientsocket.recv(1024)
                                data = data.decode('utf-8')
                                totalRecv += len(data)
                                f.write(data)
                                print ("{0: 2f}".format((totalRecv/float(tamFile))*100)+\
                                        "% Done")

                            print("Descarga Completa")
                    else:
                        print("El archivo no existe")
                #TCPClientsocket.close()
            else:
                print("\nVuelve Pronto\n")

    return resp

def modo_Server():
    listaConexiones = []
    hostS = "127.0.0.1"
    portS = 12357
    numConn = 2
    serveraddr = (hostS, int(portS))
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPServerSocket:
        TCPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        TCPServerSocket.bind(serveraddr)
        TCPServerSocket.listen(int(numConn))
        #print("El servidor TCP está disponible y en espera de solicitudes")
        servirPorSiempre(TCPServerSocket, listaConexiones)

def inicio_p2p():
        thread_read = threading.Thread(target=modo_Server, args=[])
        thread_read.start()
        modo_Usuario()

inicio_p2p()