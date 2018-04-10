import socket, glob, os, signal, sys, logging, threading
from pathlib import Path
from threading import Thread

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
BOOL = '.B'
TIME = '.T'
#sockets communication parameters
SERVER_PORT = 8060
MSG_SIZE = 1024

#global variables
sockets = []
threads = []
timeouts = {}

def login(message):
    #return send, name
    global timeouts
    splitMsg = message.split(' ')
    if len(splitMsg) != 2:
        #wrong message
        return invalidMessage(message), NULL
    else:
        timeouts[splitMsg[1]+BOOL] = False
        timeouts[splitMsg[1]+TIME] = threading.Timer(WAIT_TIME, timeout, splitMsg[1])
        return "HELLO " + splitMsg[1] , splitMsg[1]

def list():
    #return send
    #read txt files to return the list of quizes
    list = NULL
    for file in glob.glob("*"+QUIZ_EXTENSION):
        list += '\n' + file.split(QUIZ_EXTENSION)[0] #every filename is in

    if (list == NULL): #error message
        list = "there are no quizes"
    return list

def quizDo(name, quizName,  message): #load quiz to RAM
    #return send, quiz, quizName
    global timeouts
    if(name == NULL):
        return "please login first" , NULL, NULL
    if(quizName != NULL):
        return "already in a quiz, please finish it first", NULL, NULL
    splitMsg = message.split(' ')
    if len(splitMsg) != 2:
        #wrong message
        return invalidMessage(message), NULL, NULL
    else:
        my_file = Path("./" + splitMsg[1] + QUIZ_EXTENSION)
        if my_file.is_file():
            f = open(splitMsg[1]+QUIZ_EXTENSION, "r")
            file = []
            for line  in f:
                file.append(line)
            f.close()
            if len(file) == 0:
                return "empty file", NULL, NULL
            else:
                timeouts[name+BOOL] = False
                timeouts[name+TIME] = threading.Timer(WAIT_TIME, timeout, name)
                timeouts[name+TIME].start()
                return prepareQuestion(file[0]), file, splitMsg[1]
        else:
            return "no quiz named: " + splitMsg[1], NULL, NULL


def answer(name, quizName, message, quiz, question):
    #return send, question, quiz
    global timeouts
    if (quizName == NULL):
        return "no quiz selected", 0, NULL, NULL
    else:
        #check message
        splitMsg = message.split(" ")
        if len(splitMsg) != 2:
            return invalidMessage(message), question, quiz, quizName
        else:
            #get number
            number = splitMsg[1].rstrip()#remove \n
            if number != '1' and number != '2' and number != '3' and number != '4':
                return invalidMessage(message), question, quiz, quizName

            else:

                answer = quiz[question].split(":")[-1].rstrip()
                if timeouts[name+BOOL] :
                    #reached timeout
                    timeouts[name+BOOL] = False
                    logAnswer(quizName, name, question, '0', '0')
                    r = "\nTimeout!\nCorrect answer: "+ answer
                elif number == answer:
                    #correct answer
                    logAnswer(quizName, name, question, number , '1' )
                    r = "correct answer!\n"
                else:
                    #wrong answer
                    logAnswer(quizName, name, question, number , '0' )
                    r = "wrong answer, the right one is: " + message + '\n'

                question += 1 #next question
                if question == len(quiz):
                    question = 0
                    quiz= NULL
                    quizName = NULL
                    r= r +"\nEnd of quiz"
                else:
                    timeouts[name+BOOL] = False
                    timeouts[name+TIME] = threading.Timer(WAIT_TIME, timeout, name)
                    timeouts[name+TIME].start() #restart timer
                    r = r + prepareQuestion(quiz[question])

                return r , question, quiz, quizName


def skip(name, quizName, quiz, question):
    #return send, question, quiz
    global timeouts
    timeouts[name+BOOL] = False
    timeouts[name+TIME].cancel()
    if (quiz == NULL):
        return "no quiz selected", 0, quiz
    else:
        size = len(quiz)
        answer =  quiz[question].split(":")[-1].rstrip()
        showAnswer = "\ncorrect answer: "+ answer
        logAnswer(quizName, name, question, '0' , '0' )
        question += 1
        if question == size: #question is in index

            r = showAnswer + "\nEnd of quiz" , 0 , NULL
        else:
            timeouts[name+TIME] = threading.Timer(WAIT_TIME, timeout, name)
            timeouts[name+TIME].start()
            send = prepareQuestion(quiz[question])
            r = showAnswer + send, question, quiz

        return r

def quitQuiz(name, quizName, quiz, question):
    #return send, quiz, quizName, question
    global timeouts
    if(quizName != NULL):
        logAnswer(quizName, name, question, '0', '0')
        timeouts[name + TIME].cancel()
    return "Quiz quit", NULL, NULL, 0


def exit(name, quizName, quiz, question):
    #return send, game
    if(quizName != NULL):
        logAnswer(quizName, name, question, '0', '0')
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
    for client in sockets:
        print("closing client socket")
        client.shutdown(socket.SHUT_RDWR)
        #client.close() #the thread closes the socket
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
    #I use a list because it is passed by reference
    global timeouts
    timeouts[name+BOOL] = True;

def client_thread(client, addr):
    global timeouts
    name = NULL
    quiz = NULL
    quizName = NULL
    question = 0 #line of the file
    game = True

    while game:
        try:
            #receive message
            data = client.recv(MSG_SIZE)
            message = data.decode()
            print ("received message: " + '\'' + message + '\'')

            splitMsg = message.split(' ', maxsplit=1)
            command = splitMsg[0]
            #switch
            if (command == 'LOGIN'):
                send, name = login(message)
            elif(command == 'LIST'):
                send = list()
            elif(command == 'QUIZDO'):
                send, quiz, quizName = quizDo(name,quizName, message)
            elif (command =='ANSWER'):
                send, question, quiz, quizName = answer(name, quizName, message, quiz, question)
            elif (command =='SKIP'):
                send, question, quiz = skip(name, quizName, quiz, question)
            elif (command == 'QUITQUIZ'):
                send, quiz, quizName, question = quitQuiz(name, quizName, quiz)
            elif(command == 'EXIT'):
                send, game = exit(name, quizName, quiz, question)
            else:
                send = invalidMessage(message)

            #send message
            msg = send.encode()
            client.send(msg)

        except socket.error:

            print("socket error")
            game = False
            break;#break the loop
        except Exception as err:
            #print ("Unexpected error:", sys.exc_info()[0])
            logging.exception("message")
            game = False
            break;#unnecessary


    #client.shutdown(socket.SHUT_RDWR)
    if ( name != NULL):
        del timeouts[name+BOOL]
        del timeouts[name+TIME]
    print("client socket closed")
    client.close()
    sockets.remove(client)
    print("end of thread")
    #close only socket
    sys.exit(0)

#main code

#catch Ctrl+C signal
signal.signal(signal.SIGINT, signalHandler)


server_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server_sock.bind(('', SERVER_PORT))
server_sock.listen(1)
print("Server started")

while True:

    (client, addr) = server_sock.accept()
    print ('Connection address: ', addr)
    sockets.append(client)

    thread = Thread(target = client_thread, args = (client, addr))

    thread.start()
    threads.append(thread)

    #break;#debug

for thread in threads:
    thread.join()
#thread.join()
#server_sock.close()
