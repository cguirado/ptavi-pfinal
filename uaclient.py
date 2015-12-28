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
Config = sys.argv[1]
Metodo = sys.argv[2]
Opcion = sys.argv[3]
#Extraer del XML
class CrearDicc (ContentHandler):
    def __init__(self):
         self.tags = []
         self.dicc = {"account":['username','passwd'],
                      "uaserver":['ip', 'puerto'],
                      "rtpaudio":['puerto'],
                      "regproxy":['ip','puerto'],
                      "log":['path'],
                      "audio":['path']}

#Metodo para coger los elemenos
    def startElement(self, name, attrs):
        if name in self.dicc:
            dicc2={}
            for atributo in self.dicc[name]:
                #Guardar los atributos en mi diccionario
                dicc2[atributo] = attrs.get(atributo,"")
                #Añadir sin borrar
            self.tags.append([name,dicc2])

    def get_tags(self):
        return self.tags

parser = make_parser()
chandler = CrearDicc()
parser.setContentHandler(chandler)
parser.parse(open(Config))
#Aqui extraigo del xml a mi dicc
Confxml = chandler.get_tags()

#Coger  las cosas del xml en variables (si no las necesito las borro mas tarde)
username = Confxml[0][1]["username"]
contraseña = Confxml[0][1]["passwd"]
ipserv = Confxml[1][1]["ip"]
portserv = Confxml[1][1]["puerto"]
rtaudio = Confxml[2][1]["puerto"]
iproxy = Confxml[3][1]["ip"]
portproxy = Confxml[3][1]["puerto"]
log = Confxml[4][1]["path"]
audio = Confxml[5][1]["path"]


"""
Separar = Direccion.split(":")
part1 = Separar[0]
PORT = int(Separar[1])
Login = part1.split("@")[0]
IP = part1.split("@")[1]
"""
# Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
my_socket.connect((iproxy, int(portproxy)))

#Contenido que enviamos
if Metodo == "REGISTER":
    #REGISTER sip:leonard@bigbang.org:1234 SIP/2.0
    #Expires: 3600
    LINE = ("REGISTER sip:" + username + ":" + portserv + "SIP/2.0 \r\n" )
    LINE += ("Expires: " + Opcion)
if Metodo == "INVITE":
    """
INVITE sip:penny@girlnextdoor.com SIP/2.0
Content-Type: application/sdp
v=0
o=leonard@bigbang.org 127.0.0.1
s=misesion
t=0
m=audio 34543 RTP
    """
    LINE = ("INVITE sip:" + Opcion + " SIP/2.0" + "\r\n")
    LINE += ("Content-Type: application/sdp \r\n ")
    LINE += ("v=0 \r\n")
    LINE += ("o=" + username + ipserv)
    LINE += ("t=0")
    LINE += ("m= audio" + rtaudio + "RTP" )
if Metodo == "ACK":
    #No estoy segura de esto
    LINE = "200 OK ACK"
if Metodo == "BYE":
    LINE = ("BYE sip:" + username + "@" + ipserv + " SIP/2.0" + "\r\n")
if Metodo not in ["INVITE", "BYE"]:
    sys.exit("Usage: python client.py method receiver@IP:SIPport" +
             "method == INVITE o BYE" )

print("Enviando: " + LINE)
my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
#data = my_socket.recv(1024)
data = my_socket.recv(portserv)

print('Recibido -- ', data.decode('utf-8'))
Recibido = data.decode('utf-8')
Part_Recb = Recibido.split()
if Part_Recb[1] == "100" and Part_Recb[4] == "180" and Part_Recb[7] == "200":
    LINE = ("ACK sip:" + username + "@" + ipserv + " SIP/2.0" + "\r\n")
    my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
print("Terminando socket...")

# Cerramos todo
my_socket.close()
print("Fin.")
