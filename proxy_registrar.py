    #!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""
import socket
import socketserver
import sys
import json
import time
import random
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import hashlib
#Comparar argumentos
if len(sys.argv) != 2:
    error = ("Usage: python proxy_registrar.py config")
    log_fich(log, "Error", uaip, uapuerto, error)
    sys.exit(error)
#Extraemos del xml


class CrearDicc (ContentHandler):
    def __init__(self):
        self.tags = []
        self.dicc = {"server": ['name', 'ip', 'puerto'],
                     "database": ['path', 'passwdpath'],
                     "log": ['path']}

#Metodo para coger los elemenos
    def startElement(self, name, attrs):
        if name in self.dicc:
            dicc2 = {}
            for atributo in self.dicc[name]:
                #Guardar los atributos en mi diccionario
                dicc2[atributo] = attrs.get(atributo, "")
                #Añadir sin borrar
            self.tags.append([name, dicc2])

    def get_tags(self):
        return self.tags


def log_fich(fichero, metodo, ip, puerto, linea):
    Log = open(fichero, 'a')
    formato = '%Y%m%d%H%M%S'
    linea = linea.replace("\r\n", " ")
    if metodo == "Envio":
        Log.write(time.strftime(formato, time.gmtime()) +
                  ' Sent to ' + ip + ":" + str(puerto) + ': ' + linea + '\r\n')
    elif metodo == "Recibo":
        Log.write(time.strftime(formato, time.gmtime()) +
                  ' Received from ' + ip + ":" + str(puerto) +
                  ': ' + linea + '\r\n')
    elif metodo == "Error":
        Log.write(time.strftime(formato, time.gmtime()) +
                  ' Error: ' + linea + '\r\n')
    elif metodo == "Empezar":
        Log.write(time.strftime(formato, time.gmtime()) +
                  "Starting..." + '\r\n')
    elif metodo == "Final":
        Log.write(time.strftime(formato, time.gmtime()) + "Finishing" + '\r\n')
    else:
        #Para trazas mias
        Log.write(time.strftime(formato, time.gmtime()) + linea + '\r\n')
    Log.close()


def Buscarpasswd(direc):
    fichero = open(datapasswd)
    Datos = fichero.readlines()
    for linea in Datos:
        if linea != "":
                palabra = linea.split(" ")
                if palabra[0] == direc:
                    passwd = palabra[1]
    return passwd


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


class EchoHandler(socketserver.DatagramRequestHandler):
    """
    Echo server class
    """
    dicserv = {}
    diccnonce = {}

    def register2json(self):
        #Creamos fichero
        newfich = "registered.json"
        with open(newfich, 'w') as ficherojson:
            json.dump(self.dicserv, ficherojson)

    def registrados(self):
    #Usuario se registra o borrar
        if datapath == "":
            datapath = "register.txt"
            #Abrimos el fichero
        fich = open(datapath, "w")
        for usuario in self.dicserv:
            ip = self.dicserv[usuario][0]
            puerto = self.dicserv[usuario][1]
            hora = self.dicserv[usuario][2]
            tiempo = self.dicserv[usuario][3]
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
            log_fich(log, "Recibo", IP, PORT, line)
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
                puerto = rest[2]
                aleatorio = random.randint(100000000000000000000,
                                           999999999999999999999)
                if len(linea) == 5:
                    sms = ("SIP/2.0 401 Unauthorized"+"\r\n")
                    sms += ("WWW Authenticate: Digest " + "nonce= " +
                            str(aleatorio) + "\r\n")
                    self.wfile.write(bytes(sms, 'utf-8') + b"\r\n" + b"\r\n")
                    print("Enviamos al cliente: " + sms)
                    log_fich(log, "Envio", IP, PORT, sms)
                    self.diccnonce[direccion] = aleatorio
                elif len(linea) == 8:
                    contr = Buscarpasswd(direccion)
                    contr = contr[:-1]
                    Auto = linea[7].split("=")
                    Autorizar = Auto[1]
                    aletor = self.diccnonce[direccion]
                    aleatoriob = (bytes(str(aletor), 'utf-8'))
                    contrb = (bytes(contr, 'utf-8'))
                    m = hashlib.md5()
                    m.update(contrb + aleatoriob)
                    respuesta = m.hexdigest()
                    if respuesta == Autorizar:
                        sms = ("SIP/2.0 200 OK")
                        self.wfile.write(bytes(sms, 'utf-8') + b"\r\n" +
                                         b"\r\n")
                        print("Enviamos al cliente: " + sms)
                        log_fich(log, "Envio", IP, PORT, sms)
                        formato = '%Y-%m-%d %H:%M:%S'
                        valor1 = int(valor) + int(time.time())
                        tiempo = time.strftime(formato, time.gmtime(valor1))
                        if valor == "0":
                            del self.dicserv[direccion]
                        else:
                            self.dicserv[direccion] = [str(IP), puerto,
                                                       tiempo, valor]
                            lista = []
                            for usuario in self.dicserv:
                                nuevo = self.dicserv[usuario][2]
                                hor = time.gmtime(time.time())
                                if time.strptime(nuevo, formato) <= hor:
                                    lista.append(usuario)
                                    for cliente in lista:
                                        del self.dicserv[cliente]
                            self.register2json()
                    else:
                        sms = ("SIP/2.0 400 Bad Request")
                        self.wfile.write(bytes(sms, 'utf-8') + b"\r\n" +
                                         b"\r\n")
                        log_fich(log, "Error", uaip, uapuerto, sms)
            elif metodo == "INVITE":
                #Sacamos a quien queremos enviar
                dic = linea[1]
                direc = dic.split(":")[1]
                puerto = linea[11]
                if direc in self.dicserv:
                    uaip = self.dicserv[direc][0]
                    uapuerto = self.dicserv[direc][1]
        # Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
                    my_socket = socket.socket(socket.AF_INET,
                                              socket.SOCK_DGRAM)
                    my_socket.setsockopt(socket.SOL_SOCKET,
                                         socket.SO_REUSEADDR, 1)
                    my_socket.connect((uaip, int(uapuerto)))
                    #Envio el invite al servidor con el que quiero comunicarme
                    #print("Mandamos el invite al servidor")
                    my_socket.send(bytes(line, 'utf-8') + b'\r\n')
                    #print("Esperamos que nos llegue algo?")
                    data = my_socket.recv(int(uapuerto))
                    print('Recibido -- ', data.decode('utf-8'))
                    log_fich(log, "Recibo", uaip, uapuerto, line)
                    Recibido = data.decode('utf-8')
                    Part_Recb = Recibido.split()
                    log_fich(log, "Envio", uaip, uapuerto, Recibido)
                    self.wfile.write(bytes(Recibido, 'utf-8') + b"\r\n" +
                                     b"\r\n")

                else:
                    mensaje = ("SIP/2.0 404 User Not Found")
                    log_fich(log, "Error", ip, puerto, mensaje)
                    self.wfile.write(bytes(mensaje, 'utf-8') + b"\r\n" +
                                     b"\r\n")

            elif metodo == "ACK":
                dic = linea[1]
                direc = dic.split(":")[1]
                uaip = self.dicserv[direc][0]
                uapuerto = self.dicserv[direc][1]
                # Creamos socket,lo configuramos Y atamos a un servidor/puerto
                my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                my_socket.connect((uaip, int(uapuerto)))
                log_fich(log, "Envio", uaip, uapuerto, line)
                my_socket.send(bytes(line, 'utf-8') + b'\r\n')

            elif metodo == "BYE":
                dic = linea[1]
                direc = dic.split(":")[1]
                uaip = self.dicserv[direc][0]
                uapuerto = self.dicserv[direc][1]
                # Creamos el socket,lo configuramos y atamos servidor/puerto
                my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                my_socket.connect((uaip, int(uapuerto)))
                log_fich(log, "Envio", uaip, uapuerto, line)
                my_socket.send(bytes(line, 'utf-8') + b'\r\n')
                data = my_socket.recv(int(uapuerto))
                print('Recibido -- ', data.decode('utf-8'))
                Recibido = data.decode('utf-8')
                Part_Recb = Recibido.split()
                #print("Volvemos a enviar al cliente la contestacion del serv")
                self.wfile.write(bytes(Recibido, 'utf-8') + b"\r\n" + b"\r\n")

            elif metodo not in ["REGISTER", "INVITE", "BYE", "ACK"]:
                self.wfile.write(b"SIP/2.0 405 Method Not Allowed" +
                                 b"\r\n" + b"\r\n")
                error = ("SIP/2.0 405 Method Not Allowed")
                log_fich(log, "Error", ip, puerto, error)
            else:
                self.wfile.write(b"SIP/2.0 400 Bad Request" + b"\r\n" +
                                 b"\r\n")
                error = ("SIP/2.0 400 Bad Request")
                log_fich(log, "Error", ip, puerto, error)


if __name__ == "__main__":
    # Creamos servidor de eco y escuchamos
    PORT = int(puerto)
    serv = socketserver.UDPServer(('', PORT), EchoHandler)
    p = ("Empezar...")
    print("Starting...")
    log_fich(log, "Empezar", '', PORT, p)
    serv.serve_forever()
