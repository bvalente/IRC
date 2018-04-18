import socket, glob, os, signal, sys, logging
from pathlib import Path
from threading import Thread, Timer

#Version 2
'''
Commands
LOGIN       <name>
LIST
QUIZDO      <quiz name>
ANSWER      <answer number
SKIP
QUITZUIZ
EXIT
'''

#constants definition
NULL = ''
QUIZ_EXTENSION = '-quiz.txt'
LOG_EXTENSION = '-log.txt'
WAIT_TIME = 60.0

#sockets communication parameters
SERVER_PORT = 8050
MSG_SIZE = 1024

#global variables
sockets = []
threads = []
clients = {}

class Client:
    def __init__(self, name):
        self._name = name
        self._quiz = []
        self._quizName = NULL
        self._question = 0
        self._timeout = False
        self._timeThread = Timer(WAIT_TIME, timeout, name)

    def getName(self):
        return self._name
    def getQuiz(self):
        return self._quiz
    def setQuiz(self, quiz):
        self._quiz = quiz
    def getQuizName(self):
        return self._quizName
    def setQuizName(self, quizName):
        self._quizName = quizName
    def getQuestion(self):
        return self._question
    def nextQuestion(self):
        self._question += 1
        return self._question
    def resetQuiz(self):
        self._quiz = []
        self._quizName = NULL
        self._question = 0
    def getTimeout(self):
        return self._timeout
    def reachTimeout(self):
        self._timeout = True
    def stopTimer(self):
        self._timeout = False
        self._timeThread.cancel()
    def startTimer(self):
        self._timeThread = Timer(WAIT_TIME, timeout, [self._name])
        #print("name: " + self._name)
        self._timeThread.start()

def login(message, serverName):
    splitMsg = message.split(' ')
    if len(splitMsg) != 2:
        #wrong message
        return invalidMessage(message), serverName
    else:
        name = splitMsg[1]
        if name in clients:
            return "name already registered", serverName
        elif serverName != NULL:
            return "player "+ serverName + " already logged in", serverName
        else:
            #create new client
            clients[name] = Client(name)
            return "HELLO " + name , name

def list():
    #read txt files to return the list of quizes
    list = NULL
    for file in glob.glob("*"+QUIZ_EXTENSION):
        list += '\n' + file.split(QUIZ_EXTENSION)[0] #every filename is in

    if (list == NULL): #error message
        list = "there are no quizes"
    return list

def quizDo(name, message): #load quiz to RAM
    if(name == NULL):
        return "please login first"
    player = clients[name]
    if(player.getQuizName() != NULL or player.getQuiz() != []):
        return "already in a quiz, please finish it first"

    splitMsg = message.split(' ')
    if len(splitMsg) != 2:
        #wrong message
        return invalidMessage(message)
    else:
        quizName = splitMsg[1]
        my_file = Path("./" + quizName + QUIZ_EXTENSION)
        if my_file.is_file():
            f = open(quizName+QUIZ_EXTENSION, "r")
            file = []
            for line  in f:
                file.append(line)
            f.close()
            if len(file) == 0:
                return "empty file"
            else:
                player.startTimer()
                player.setQuiz(file)
                player.setQuizName(quizName)
                return prepareQuestion(file[0])
        else:
            return "no quiz named: " + quizName

def answer(name, message):
    if name == NULL:
        return "please login first"
    player = clients[name]
    quizName = player.getQuizName()
    quiz = player.getQuiz()
    question = player.getQuestion()
    if (quizName == NULL):
        return "no quiz selected"
    #check message
    splitMsg = message.split(" ")
    if len(splitMsg) != 2:
        return invalidMessage(message)
    #get number
    number = splitMsg[1].strip('\n')#remove \n
    if number != '1' and number != '2' and number != '3' and number != '4':
        return invalidMessage(message)

    answer = quiz[question].split(":")[-1].rstrip()
    if player.getTimeout() :
        #reached timeout
        player.stopTimer()
        logAnswer(quizName, name, question, '0', '0')
        r = "\nTimeout!\nCorrect answer: " + answer +'\n'
    elif number == answer:
        #correct answer
        logAnswer(quizName, name, question, number , '1' )
        r = "correct answer!" + '\n'
    else:
        #wrong answer
        logAnswer(quizName, name, question, number , '0' )
        r = "wrong answer, the right one is: " + answer+ '\n'
    player.stopTimer()
    question = player.nextQuestion()
    if question == len(quiz):
        player.resetQuiz()
        r = r +"End of quiz"
    else:
        player.startTimer()
        r = r + prepareQuestion(quiz[question])

    return r

def skip(name):
    if name == NULL:
        return "please login first"
    player = clients[name]
    player.stopTimer()
    quiz = player.getQuiz()
    if (quiz == [] or player.getQuizName() == NULL):
        return "no quiz selected"
    else:
        size = len(quiz)
        question = player.getQuestion()
        answer =  quiz[question].split(":")[-1].rstrip()
        showAnswer = "\nCorrect answer: "+ answer
        logAnswer(player.getQuizName(), name, question, '0' , '0' )
        question = player.nextQuestion()
        if question == size: #question is in index
            player.resetQuiz()
            return showAnswer + "\nEnd of quiz"
        else:
            player.startTimer()
            return showAnswer + prepareQuestion(quiz[question])

def quitQuiz(name):
    if name == NULL:
        return "please login first"
    player = clients[name]
    if(player.getQuizName() != NULL):
        logAnswer(player.getQuizName(), name, player.getQuestion(), '0', '0')
        player.stopTimer()
        player.resetQuiz()
        return "Quiz quit"
    else:
        return "Not in a quiz"

def exit(name):
    quitQuiz(name)
    return 'DIE', False

def invalidMessage(message):
    return 'Invalid message: ' + '\'' + message + '\''

def logAnswer(quizName,name, question, answer, correct ):
    f = open(quizName + LOG_EXTENSION, 'a')
    f.write(name +':'+ str(question+1) +':'+ answer +':'+ correct + '\n')
    f.close()

def prepareQuestion(message):
    splitMsg = message.split(":")
    size = len(splitMsg)
    question = NULL
    for i in range(0, size-1):
        if i == 0:
            question += '\n' +"Question: "+ splitMsg[i]
        else:
            question += '\n' + str(i) +": " + splitMsg[i]
    return question

def signalHandler(signal, frame):
    print("Signal catched")
    #close every socket
    for sock in sockets:
        print("closing client socket")
        sock.shutdown(socket.SHUT_RDWR)
    #close server socket
    print("closing server socket")
    server_sock.close()
    #join every thread
    for thread in threads:
        print("joining thread")
        thread.join()
    #exit program
    print("exit program")
    sys.exit(0)

def timeout(name):
    clients[name].reachTimeout()

def client_thread(sock, addr):
    name = NULL
    game = True

    while game:
        try:
            #receive message
            data = sock.recv(MSG_SIZE)
            message = data.decode()
            print ("received message: " + '\'' + message + '\'')

            splitMsg = message.split(' ', maxsplit=1)
            command = splitMsg[0]
            #switch
            if (command == 'LOGIN'):
                send, name = login(message, name)
            elif(command == 'LIST'):
                send = list()
            elif(command == 'QUIZDO'):
                send = quizDo(name, message)
            elif (command =='ANSWER'):
                send = answer(name, message)
            elif (command =='SKIP'):
                send = skip(name)
            elif (command == 'QUITQUIZ'):
                send = quitQuiz(name)
            elif(command == 'EXIT'):
                send, game = exit(name)
            else:
                send = invalidMessage(message)

            #send message
            msg = send.encode()
            sock.send(msg)

        except socket.error:
            print("socket error")
            game = False

        except Exception as err:
            logging.exception("message")
            game = False
    if name != NULL:
        del clients[name] #remove player from list
    print("client socket closed")
    sock.close()
    sockets.remove(sock)
    print("end of thread")
    sys.exit(0)

#main code

#catch Ctrl+C signal
signal.signal(signal.SIGINT, signalHandler)
#create server socket
server_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server_sock.bind(('', SERVER_PORT))
server_sock.listen(1)
print("Server started")

while True:

    (sock, addr) = server_sock.accept()
    print ('Connection address: ', addr)
    sockets.append(sock)

    thread = Thread(target = client_thread, args = (sock, addr))
    thread.start()
    threads.append(thread)

print("Major error")
