# UDP Client for test
import socket
import struct

def send(score:int):

    host = '169.254.95.244'
    port = 8888
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        # send data to server
        val = struct.pack('!i', score)
        sock.sendto(val, (host, port))
        #print('[ SENT ]')

    except OSError as err:
        print(err)


