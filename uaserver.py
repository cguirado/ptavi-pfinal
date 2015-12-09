#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

import socketserver
import sys
import os
import os.path

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
            (metodo, direccion, elresto) = line.split()
            if metodo == "INVITE":
                self.wfile.write(b"SIP/2.0 100 Trying"+b"\r\n"+b"\r\n")
                self.wfile.write(b"SIP/2.0 180 Ring"+b"\r\n"+b"\r\n")
                self.wfile.write(b"SIP/2.0 200 OK"+b"\r\n"+b"\r\n")
            elif metodo == "BYE":
                self.wfile.write(b"SIP/2.0 200 OK"+b"\r\n"+b"\r\n")
            elif metodo == "ACK":
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
    if len(sys.argv) != 4:
       sys.exit("Usage: python server.py IP port audio_file")
    PORT = int(sys.argv[2])
    IP = sys.argv[1]
    Fichero = sys.argv[3]
    if not os.path.exists (Fichero):
        sys.exit("Usage: python server.py IP port audio_file")
    serv = socketserver.UDPServer((IP, int(PORT)), EchoHandler)
    print("Listening...")
    serv.serve_forever()
