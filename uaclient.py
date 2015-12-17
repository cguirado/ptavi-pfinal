#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Programa cliente que abre un socket a un servidor
"""

import socket
import sys
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

# Cliente UDP simple.

#Comparar argumentos
if len(sys.argv) != 4:
    sys.exit("Usage: python client.py config method opcion")
# Dirección IP del servidor.
SERVER = 'localhost'
Config = sys.argv[2]
Metodo = sys.argv[3]
Opcion = sys.argv[4]
#Extraer del XML
class CrearDicc (ContentHandler)
    def __init__(self):
         self.tags = []
         self.dicc = {"account":['username','passwd'],
                      "uaserver":['ip', 'puerto'],
                      "rtpaudio":['puerto'],
                      "regproxy":['ip','puerto'],
                      "log":['path'],
                      "audio":['path']}

    def startElement(self, name, attrs):
        if name in self.dicc:
            dicc2={}
            for atributo in self.dicc[name]:
                dicc2[atributo] = attrs.get(atributo,"")
            self.tags.append([name,dicc2])

    def get_tags(self):
        return self.tags

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
