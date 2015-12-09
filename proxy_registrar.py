#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

import socketserver
import sys
import json
import time


class EchoHandler(socketserver.DatagramRequestHandler):
    """
    Echo server class
    """
    dicserv = {}

    def register2json(self):
        """
        Creamos fichero json
        """
        newfich = "registered.json"
        with open(newfich, 'w') as ficherojson:
            json.dump(self.dicserv, ficherojson)

    def json2registered(self):
        """
        Si tenemos fichero json lo leemos
        """
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
            self.wfile.write(b"SIP/2.0 200 OK"+b"\r\n"+b"\r\n")
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            lineb = self.rfile.read()
            print("El cliente nos manda " + lineb.decode('utf-8'))
            line = lineb.decode('utf-8')
            if not line:  # Si no hay más líneas salimos del bucle infinito
                break
            (metodo, direccion, elresto, expire, valor) = line.split()
            if metodo != "REGISTER" and not "@" in direccion:
                break
            formato = '%Y-%m-%d %H:%M:%S'
            valor1 = int(valor) + int(time.time())
            tiempo = time.strftime(formato, time.gmtime(valor1))
            if int(valor) == 0:
                del self.dicserv[direccion]
            else:
                USER = direccion.split(":")[1]
                self.dicserv[direccion] = [str(IP), tiempo]
            self.wfile.write(b"SIP/2.0 200 OK"+b"\r\n"+b"\r\n")

            lista = []
            print(self.dicserv)
            for usuario in self.dicserv:
                nuevo = self.dicserv[usuario][1]
                if time.strptime(nuevo, formato) <= time.gmtime(time.time()):
                    lista.append(usuario)
            for cliente in lista:
                del self.dicserv[cliente]
            self.register2json()
if __name__ == "__main__":
    # Creamos servidor de eco y escuchamos
    PORT = int(sys.argv[1])
    serv = socketserver.UDPServer(('', PORT), EchoHandler)
    print("Lanzando servidor UDP de eco...")
    serv.serve_forever()
