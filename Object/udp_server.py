# UDP Server for test

import socket
import struct

UDP_IP_ADDRESS = "0.0.0.0"

UDP_PORT_NO = 8888
serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSock.bind((UDP_IP_ADDRESS, UDP_PORT_NO))

while True:
    data, addr = serverSock.recvfrom(1024)
    received = struct.unpack('!i', data[:4])[0]
 
    print ("Score:", received)


