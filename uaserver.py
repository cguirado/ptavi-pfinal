#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

import socketserver
import sys
import os
import os.path
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
# Creamos servidor de eco y escuchamos
if len(sys.argv) != 2:
   sys.exit("Usage: python server.py config")
Config = sys.argv[1]
#Extraemos del xml
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



class EchoHandler(socketserver.DatagramRequestHandler):
    """
    Echo server class
    """

    def handle(self):
        # Escribe dirección y puerto del cliente (de tupla client_address)
        IP = self.client_address[0]
        PORT = self.client_address[1]
        print("IP: ", IP)
        print("Puerto: ", PORT)

        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            lineb = self.rfile.read()
            if not lineb:
                break
            print("El cliente nos manda " + lineb.decode('utf-8'))
            line = lineb.decode('utf-8')
            print (line)
            linea = line.split()
            metodo = linea[0]
            print("LLEGAAAAA",metodo)
            print("METODO", metodo, linea)
            #(metodo, direccion, elresto) = line.split()
            if metodo == "INVITE":
                self.wfile.write(b"SIP/2.0 100 Trying"+b"\r\n"+b"\r\n")
                self.wfile.write(b"SIP/2.0 180 Ring"+b"\r\n"+b"\r\n")
                self.wfile.write(b"SIP/2.0 200 OK"+b"\r\n"+b"\r\n")
            elif metodo == "BYE":
                self.wfile.write(b"SIP/2.0 200 OK"+b"\r\n"+b"\r\n")
            elif metodo == "ACK":
                print("Llega??")
                Ejecutar = "./mp32rtp -i " + IP + " -p 23032 <" + sys.argv[3]
                os.system(Ejecutar)
            elif metodo not in ["INVITE", "BYE", "ACK"]:
                self.wfile.write(b"SIP/2.0 405 Method Not Allowed" +
                                 b"\r\n"+b"\r\n")
            else:
                self.wfile.write(b"SIP/2.0 400 Bad Request"+b"\r\n"+b"\r\n")
            # Si no hay más líneas salimos del bucle infinito


if __name__ == "__main__":
    # Creamos servidor de eco y escuchamos
    if not os.path.exists (Config):
        sys.exit("Usage: python server.py IP port audio_file")
    serv = socketserver.UDPServer((ipserv, int(portserv)), EchoHandler)
    print("Listening...")
    serv.serve_forever()
