import socket
import os.path
import glob, os

### addQuestion not totally implemented ####

#sockets communication parameters
SERVER_PORT = 12002
MSG_SIZE = 1024

#message info
TYPE = 0
QUIZNAME = 1
QUESTION = 2
ANSWERS = 3

#other constants
QUIZEXTENSION = '-quiz.txt'


server_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server_sock.bind(('', SERVER_PORT))
server_sock.listen(5) #connected clients?
(client, addr) = server_sock.accept()
print ('Connection address:', addr)


def write_file(quizName, text):
    file = open(quizName, 'a')
    file.write(text)
    file.close()

def file_exists(fileName):
    name = fileName + QUIZEXTENSION
    try:
        file = open(name, 'r') #
        file.close()
        return False
    except IOError:
        file = open(name, 'w')
        file.close()
        return True
def sendMessage(text):
    if text != '':
        msg = text
    else:
        print('else')
        msg = 'Message is empty'
    msg_sent = msg.encode()
    client.send(msg_sent)

def rcvMessage():
    data = client.recv(MSG_SIZE)
    msg_rcv = data.decode()
    msg_rcv = msg_rcv.strip('\n')
    return msg_rcv

def isInt(n):
    try:
        int(i)
    except:
        return False
    return True

def addQuestion(quizName):

    name = quizName + QUIZEXTENSION
    try:
        print('OPENED')
        with open(name) as f:
            line = f.readlines()
            f.close()
    except IOError:
        print('ierror')
        return 'Quiz not registered'

    print('trying to send')
    sendMessage('What is the question you would like to add?')

    data = rcvMessage()

    emptyString = False

    if len(data)==0:
        print('UUU')
        emptyString = True

    while emptyString:

        sendMessage('Choose another question')
        data = rcvMessage()
        if len(data) != 0:
            print('accepted format')
            break

    data.strip('\n')

    if data in line:
        print('QUESTION EXISTS')
        return 'Question already exists' #nothings written

    else:
        #escrever a pergunta
        f = open(name, 'a')
        if len(line) == 0:
            f.write(data + ':')
        else:
            f.write('\n' + data + ':')
        f.close()

        sendMessage('Question registered. Add an answer:')

        f = open(name, 'a')

        i = 0
        var = True
        while var: #max 5 iterations and
            print('lixo')
            answer = rcvMessage()

            if i < 4:

                if len(answer) == 0:
                    sendMessage('Empty answer entered, try again')
                    i -= 1
                    continue

                elif len(answer) > 0:
                    f.write(answer + ':')
                    if (i >= 2):
                        new = '(last argument is the number of the correct Answer)'
                    else:
                        new = ''
                    sendMessage('Add another answer:' + new)

                elif isInt(answer) and i >= 2:
                    print('here')
                    f.write(answer + '\n')
                    return 'Question added'
            else:
                var = False
            print(i)
            i += 1
        f.close()
    return 'Done'

def newQuiz(fileName):
    if (file_exists(fileName)):
        server_msg = 'Created Quiz'
    else:
        server_msg = 'Choose another quiz name'

    return server_msg

def listQuiz():

    dirpath = os.getcwd()
    print(dirpath)
    os.chdir(dirpath)
    str = 'List of Quizzes\n'

    for file in glob.glob("*-quiz.txt"):
        str += '- '+ file +'\n'

    str = str.replace(QUIZEXTENSION, "")

    return str

def showQuiz(quizName):
    str = 'This is the ' + quizName + ' quiz.\n'
    name = quizName + QUIZEXTENSION
    str = ''
    try:
        with open(name) as f:
            line = f.readlines()
    except IOError:
        return 'Quiz not registered'
    i=0

    while i < len(line):
        str += line[i]
        i+=1
    if (str == ''):
        return 'Quiz is Empty'
    return str

def listOptions():
    str = 'The Following functions are available\n'
    str += 'NQ: newQuiz <quizName> \n'
    str += 'SQ: showQuiz <quizName>\n'
    str += 'LQ: listQuiz <quizName>\n'
    str += 'ADDQ: addQuestion <quizName> <question> <answers(2-4) + <Right option>>'
    return str

while True:

    #receive messagem from client
    print('Waiting for instruction')
    data = client.recv(MSG_SIZE)
    request = data.decode().split()

    if len(request) == 0:
        msg = 'Enter "h" for help.'
        msg_sent = msg.encode()
        client.send(msg_sent)
        break

    request_type = request[TYPE]


    if(request_type == 'NQ' and len(request) == 2):
        name = request[QUIZNAME]
        msg = newQuiz(name)


    elif(request_type == 'ADDQ' and len(request) == 2):
        name = request[QUIZNAME]
        try:
            msg = addQuestion(name)
        except:
            print('Erro, except')
            msg = 'erro'


    elif (request_type == 'LQ' and len(request) == 1):
        msg = listQuiz()

    elif (request_type == 'SQ' and len(request) == 2):
        quizName = request[QUIZNAME]
        name = str(quizName)
        msg = showQuiz(name)
    elif(request_type == 'h' and len(request) == 1):
        msg = listOptions()

    else:
        msg = 'Invalid Function: Enter "h" for help.'

    msg_sent = msg.encode()
    client.send(msg_sent)

server_sock.close()

    #send message to client
