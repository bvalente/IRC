import socket
import sys
import select
#create a TCP socket to communicate with server


#sockets communication parameters
SERVER_PORT = 12001
SERVER_IP   = '127.0.0.1'
MSG_SIZE = 1024
NULL=''
client_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #TCP socket
client_sock.connect((SERVER_IP, SERVER_PORT))

while True:
    try :

        #send message
        print('Input message to server:')
        user_msg = sys.stdin.readline()
        if user_msg != NULL and user_msg != '\n' and user_msg != '\t':
            client_msg = user_msg.encode()
            client_sock.send(client_msg)

        #receive message
            data = client_sock.recv(MSG_SIZE)
            rcv_msg = data.decode()
            print(rcv_msg)

    except socket.error:

        print("Socket Error")
        break

print("End of Program")
