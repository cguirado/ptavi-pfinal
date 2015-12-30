#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

import socketserver
import sys
import json
import time
import random
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
#Comparar argumentos
if len(sys.argv) != 2:
    sys.exit("Usage: python proxy_registrar.py config")

#Extraemos del xml
class CrearDicc (ContentHandler):
    def __init__(self):
         self.tags = []
         self.dicc = {"server":['name','ip','puerto'],
                      "database":['path', 'passwdpath'],
                      "log":['path']}

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
parser.parse(open(sys.argv[1]))
#Aqui extraigo del xml a mi dicc mas variables
Confxml = chandler.get_tags()
name = Confxml[0][1]["name"]
ip = Confxml[0][1]["ip"]
puerto = Confxml[0][1]["puerto"]
datapath = Confxml[1][1]["path"]
datapasswd = Confxml[1][1]["passwdpath"]
log = Confxml[2][1]["path"]
if ip == "":
    ip = ("127.0.0.1")

'''
# Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
my_socket.connect((iproxy, int(portproxy)))
'''


class EchoHandler(socketserver.DatagramRequestHandler):
    """
    Echo server class
    """
    dicserv = {}

    def register2json(self):
        #Creamos fichero

        newfich = "registered.json"
        with open(newfich, 'w') as ficherojson:
            json.dump(self.dicserv, ficherojson)
    def registrados (self):
    #Usuario se registra o borrar
        if datapath == "":
            datapath = "register.txt"
            #Abrimos el fichero
        fich = open(datapath,"w")
        for usuario in self.dicserv:
            ip = self.dicserv [usuario][0]
            puerto = self.dicserv [usuario][1]
            hora = self.dicserv [usuario][2]
            tiempo = self.dicserv [usuario][3]
            # escribir en el fichero
            fich.write(usuario + " " + ip + " " + puerto
                    + " " + hora + " " + tiempo)

    def json2registered(self):
        try:
            with open("registered.json", 'r') as existe:
                self.dicserv = json.load(existe)
        except:
            pass

    def handle(self):
        """
        Donde  nos llega lo que el cliente nos envia  eliminamos, er
        """
        IP = self.client_address[0]
        PORT = self.client_address[1]
        print("IP: ", IP)
        print("Puerto: ", PORT)
        if len(self.dicserv) == 0:
            self.json2registered()
            #self.wfile.write(b"SIP/2.0 200 OK"+b"\r\n"+b"\r\n")
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            lineb = self.rfile.read()
            print("El cliente nos manda " + lineb.decode('utf-8'))
            line = lineb.decode('utf-8')
            linea = line.split()

            if not linea:  # Si no hay más líneas salimos del bucle infinito
                break
                #metodo = ["REGISTER", "ACK","INVITE", "BYE"]
            metodo = linea[0]
            if metodo == "REGISTER":
                #Sacado las cosas que nos interesa de la lina para el register
                #print("Comienza REGISTER")
                valor = linea[4]
                resto = linea[1]
                rest = resto.split(":")
                direccion = rest[1]
                puerto =  rest[2]
                aleatorio = random.randint(70000000,80000000)
                if len(linea)==5:
                    print("Falta el nonce para autorizar registro")
                    sms = ("SIP/2.0 401 Unauthorized"+"\r\n")
                    sms += ("WWW Authenticate: "+ "nonce= "+ str(aleatorio) + "\r\n")
                    self.wfile.write(bytes (sms,'utf-8') +b"\r\n"+b"\r\n")
                    print("Enviamos al cliente: " + sms)
                elif len(linea) == 7:
                    print("Autorizamos registro")
                    formato = '%Y-%m-%d %H:%M:%S'
                    valor1 = int(valor) + int(time.time())
                    tiempo = time.strftime(formato, time.gmtime(valor1))
                    if valor == 0:
                        del self.dicserv[direccion]
                    else:
                        #USER = direccion.split(":")[1]
                        self.dicserv[direccion] = [str(IP), puerto, tiempo, valor]
                        #self.wfile.write(b"SIP/2.0 200 OK"+b"\r\n"+b"\r\n")
                        lista = []
                        print("AQUI",self.dicserv)
                        for usuario in self.dicserv:
                            nuevo = self.dicserv[usuario][2]
                            if time.strptime(nuevo, formato) <= time.gmtime(time.time()):
                                lista.append(usuario)
                                for cliente in lista:
                                    del self.dicserv[cliente]
                                self.register2json()



            if metodo == "INVITE":
                print ("comienza INVITE")
                #Sacamos a quien queremos enviar
                dic = linea[1]
                direccion = dic.split(":")[1]
                puerto = linea[13]
                if direccion in self.diccserv:
                    uaip = self.diccserv[direccion][0]
                    uapuerto = self.diccserv[direccion][1]
                # Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
                my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                my_socket.connect((uaip, int(uaproxy)))
                #Envio el invite al servidor con el que quiero comunicarme!!
                my_socket.send(line)





if __name__ == "__main__":
    # Creamos servidor de eco y escuchamos
    PORT = int(puerto)
    serv = socketserver.UDPServer(('', PORT), EchoHandler)
    print("Lanzando servidor UDP de eco...")
    serv.serve_forever()
