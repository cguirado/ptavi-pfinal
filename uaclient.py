#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Programa cliente que abre un socket a un servidor
"""

import socket
import sys

# Cliente UDP simple.

#Comparar argumentos
if len(sys.argv) != 3:
    sys.exit("Usage: python client.py method receiver@IP:SIPport")
# Dirección IP del servidor.
SERVER = 'localhost'
Metodo = sys.argv[1]
Direccion = sys.argv[2]

Separar = Direccion.split(":")
part1 = Separar[0]
PORT = int(Separar[1])
Login = part1.split("@")[0]
IP = part1.split("@")[1]

# Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
my_socket.connect((SERVER, PORT))

#Contenido que enviamos

if Metodo == "INVITE":
    LINE = ("INVITE sip:" + Login + "@" + IP + " SIP/2.0" + "\r\n")
if Metodo == "BYE":
    LINE = ("BYE sip:" + Login + "@" + IP + " SIP/2.0" + "\r\n")
if Metodo not in ["INVITE", "BYE"]:
    sys.exit("Usage: python client.py method receiver@IP:SIPport" +
             "method == INVITE o BYE" )

print("Enviando: " + LINE)
my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
data = my_socket.recv(1024)

print('Recibido -- ', data.decode('utf-8'))
Recibido = data.decode('utf-8')
Part_Recb = Recibido.split()
if Part_Recb[1] == "100" and Part_Recb[4] == "180" and Part_Recb[7] == "200":
    LINE = ("ACK sip:" + Login + "@" + IP + " SIP/2.0" + "\r\n")
    my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
print("Terminando socket...")

# Cerramos todo
my_socket.close()
print("Fin.")
