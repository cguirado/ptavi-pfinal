#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Programa cliente que abre un socket a un servidor
"""

import socket
import sys
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import random
import hashlib
import os
import os.path

# Cliente UDP simple.


#Comparar argumentos
if len(sys.argv) != 4:
    sys.exit("Usage: python client.py config method opcion")
# Dirección IP del servidor.
SERVER = 'localhost'
Config = sys.argv[1]
Metodo = sys.argv[2]
Opcion = sys.argv[3]
aleatorio = random.randint(100000000000000000000,999999999999999999999)
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
"""
#Log fu

def log_fich(fichero,metodo,ip,puerto,linea):
    Log = open(fichero,'a')
    formato = '%Y-%m-%d %H:%M:%S'
    if metodo == "Envio":
        Log.write(time.strptime(formato,time.gmtime()) + 'Sent to ' + ip + ":" + str(puerto) +
                ': ' +  linea)
    elif metodo == "Recibo":
        Log.write(time.strptime(formato,time.gmtime()) + 'Received from ' + ip + ":" + str(puerto) +
                ': ' +  linea)
    elif metodo == "Error":
        Log.write(time.strptime(formato,time.gmtime()) + 'Error: ' +  linea)
    elif metodo == "otro":
        Log.write(time.strptime(formato,time.gmtime()) + linea)
    elif metodo == "Empezar":
        Log.write(time.strptime(formato,time.gmtime()) + linea)
    elif metodo == "Final":
        Log.write(time.strptime(formato,time.gmtime()) + linea)
    Log.close()
"""


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

# Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
my_socket.connect((iproxy, int(portproxy)))
try:
    #Contenido que enviamos
    if Metodo == "REGISTER":
        #REGISTER sip:leonard@bigbang.org:1234 SIP/2.0
        #Expires: 3600
        LINE = ("REGISTER sip:" + username + ":" + portserv + " SIP/2.0 \r\n" )
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
        LINE += ("Content-Type: application/sdp \r\n\r\n ")
        LINE += ("v=0 \r\n")
        LINE += ("o= " + username + " " + ipserv + "\r\n" )
        LINE += ("t=0" + "\r\n")
        LINE += ("m = audio " + rtaudio + " RTP \r\n")
    if Metodo == "ACK":
        #No estoy segura de esto
        LINE = "ACK sip: " + Opcion + "SIP/2.0"
        print(LINE)

    if Metodo == "BYE":
        LINE = ("BYE sip:" + Opcion + " SIP/2.0" + "\r\n")

        """
        Creo que seria asi
        """
    if Metodo not in ["INVITE", "BYE", "ACK","REGISTER"]:
        sys.exit("SIP/2.0 Bad Request" )
    #log_fich(log,"Envio",iproxy,portproxy,LINE)
    print("Enviando: " + LINE)
    my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
    data = my_socket.recv(int(portproxy))

    print('Recibido -- ', data.decode('utf-8'))
    Recibido = data.decode('utf-8')
    #Si rebibo 7 cosas del Register  y la segunda que recibo es 401
    #debo enviar otra vez register
    reciv = Recibido.split()
    print(reciv)
    if reciv[1] == "401":
        #Cuando me mandan un 401
        nonce = reciv[6]
        nonceb = (bytes(nonce,'utf-8'))
        contraseñab = (bytes(contraseña,'utf-8'))
        m = hashlib.md5()
        m.update(contraseñab + nonceb)
        respuesta = m.hexdigest()
        print("Debo volver a enviar REGISTER + autori...")
        LINE = ("REGISTER sip:" + username + ":" + portserv + " SIP/2.0 \r\n" )
        LINE += ("Expires: " + Opcion + "\r\n")
        LINE += ("Autorization: response=" + str(respuesta))
        print("Enviando: " + LINE)
        my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
        data = my_socket.recv(int(portproxy))
        #Tengo que solucionar esto!
    elif reciv[1] == "404":
        print("no registrado el usuario")
    print('Recibido -- ', data.decode('utf-8'))
    Recibido = data.decode('utf-8')
    reciv = Recibido.split()
    if reciv[1] == "100" and reciv[4]=="180" and reciv[7] == "200":
        #Saco ip y puerto del servidor
            ip_serv = reciv[14]
            puerto_serv = reciv[19]
            print("Contestar ACK", Recibido)
            LINE = ("ACK sip:" + Opcion + " SIP/2.0 \r\n" )
            print("Enviando: " + LINE)
            my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
            print("Envio RTP", ip_serv,puerto_serv)
            Ejecutar = "./mp32rtp -i " + ipserv + " -p "
            Ejecutar += puerto_serv + " < " + audio
            os.system(Ejecutar)
            print("Termina RTP")
    """
    # Escuhchar el RTP
    print("Escuchamos el RTP ")
    cvlc rtp://@:rtpaudio> /dev/null
    """
    print("Terminando socket...")
     # Cerramos todo
    my_socket.close()
    print("Fin.")
except socket.error:
    print("Error: No server listening at ", iproxy, "port ", portproxy)
