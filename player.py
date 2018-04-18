import socket, sys, select, signal

commands = '''
Commands
LOGIN       <name>
LIST
QUIZDO      <quiz name>
ANSWER      <answer number
SKIP
QUITZUIZ
EXIT
'''

#sockets communication parameters
SERVER_PORT = 8050
SERVER_IP   = '127.0.0.1'
MSG_SIZE = 1024

#global variables
NULL = ''
verbose = True
game = True

#TCP socket
client_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

#connect to server
client_sock.connect((SERVER_IP, SERVER_PORT))

def signalHandler(signal, frame):
    print("Signal catched")
    print("close socket")
    client_sock.shutdown(socket.SHUT_RDWR)
    client_sock.close()
    print("exit program")
    sys.exit(0)

def isValid(message): #not used, ready to delete
    return message != NULL and message != '\n' and message != '\t'

def sendMessage( message ):
    global client_sock
    #make sure
    while True:
        user_msg = input(message)
        if (isValid(user_msg)):
            break;
    client_msg = user_msg.encode()
    client_sock.send(client_msg)

def recvMessage():
    global client_sock, game

    server_msg = client_sock.recv(MSG_SIZE)
    message = server_msg.decode()
    #maybe I should always print the message
    if (message == 'DIE'):
        game = False
    if (verbose):
        print("Message received from server: ", message)

#main

#catch Ctrl+C signal
signal.signal(signal.SIGINT, signalHandler)

#main loop
print (commands)
while game:
    try :
        #send message to server
        sendMessage('Input message to server: ')

        #receive message from server
        recvMessage()

    except socket.error:

        print("socket error")
        break

#close socket
client_sock.close()
#end program
print("End of program")
