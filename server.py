import socket
import sys

# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#Bind the socket to the port
server_address = ('192.168.0.238',8888)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

while True:
    #print("\n waiting to receive message\n")
    data, address = sock.recvfrom(4096)

    print('received {} bytes from {}'.format(len(data),address),data)