# UDP client class for DDD project

import socket
from datetime import datetime

class UDPClient:
    ''' A simple UDP Client '''

    def __init__(self, host, port):
        self.host = host    # Host address
        self.port = port    # Host port
        self.sock = None    # Socket

    def printwt(self, msg):
        ''' Print message with current date and time '''

        current_date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f'[{current_date_time}] {msg}')

    def configure_client(self):
        ''' Configure the client to use UDP protocol with IPv4 addressing '''

        # create UDP socket with IPv4 addressing
        self.printwt('Creating UDP/IPv4 socket ...')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.printwt('Socket created')

    def interact_with_server(self):
        ''' Send request to a UDP Server and receive reply from it. '''

        try:

            # send data to server
            self.printwt('Sending name to server to get phone number ...')
            name = 'Bob'
            self.sock.sendto(name.encode('utf-8'), (self.host, self.port))
            self.printwt('[ SENT ]')
            print('\n', name, '\n')

            # receive data from server
            resp, server_address = self.sock.recvfrom(1024)
            self.printwt('[ RECEIVED ]')
            print('\n', resp.decode(), '\n')

            self.printwt('Interaction completed successfully...')

        except OSError as err:
            print(err)

        finally:
            # close socket
            self.printwt('Closing socket...')
            self.sock.close()
            self.printwt('Socket closed')

def main():
    ''' Create a UDP Client, send message to a UDP Server and receive reply. '''

    udp_client = UDPClient('192.168.86.86', 8888)
    udp_client.configure_client()
    udp_client.interact_with_server()

if __name__ == '__main__':
    main()
