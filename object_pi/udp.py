# UDP Client for test
import socket
import struct

def send(score:int):

    host = '169.254.95.244'
    port = 8888
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    result = [3,1,0]

    try:
        # send data to server
        #val = struct.pack('!i', score)
        #sock.sendto(val, (host, port))
        #print('[ SENT ]')
        
        result[2] = score
        message = str(result).encode()
        sock.sendto(message, (host, port))

    except OSError as err:
        print(err)


