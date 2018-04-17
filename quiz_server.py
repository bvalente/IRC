import socket
import os.path
import glob, os

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


def addQuestion(quizName,questionst,answerst):
    respostas = answerst.split(':')
    i = respostas[-1]

    try:
        int(i)
        integer = int(i)

    except ValueError:
        return 'ANSWERS: Last element has to be an integer'


    text = questionst + ':' + answerst + '\n'
    name = quizName + QUIZEXTENSION
    try:
        with open(name) as f:
            line = f.readlines()
    except IOError:
        return 'Quiz not registered'

    if (text in line):
        return 'Question already exists'

    if (3 <= len(respostas) <= 5 and integer < len(respostas)):
        write_file(name,text)
        return 'Created Question'

    return 'ANSWERS: Wrong arguments'

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
    str += 'ADDQ: addQuestion <quizName> <question> <answers(2-4)<Right option>>\n (Question should be followed by answers, separated with :)'
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

    #Para adicionar uma questao a um dado quiz o input deve ser do genero:
    # ADDQ quizName pergunta respostas:separadas:por:2pontos:3
    # 3 seria considerada a resposta certa.
    elif(request_type == 'ADDQ' and len(request) == 4):
        name = request[QUIZNAME]
        question = request[QUESTION]
        answers = request[ANSWERS]

        try:

            msg = addQuestion(name,question,answers)

        except:
            msg = 'Wrong arguments'

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

server_socket.close()

    #send message to client
