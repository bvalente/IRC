import socket
import os.path
import glob, os

#sockets communication parameters
SERVER_PORT = 12002
MSG_SIZE = 1024
TYPE = 0

server_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server_sock.bind(('', SERVER_PORT))
server_sock.listen(1) #connected clients?
(client, addr) = server_sock.accept()
print ('Connection address:', addr)

def list_quizes():
    way = os.getcwd()
    os.chdir(way)
    str = 'Quiz List\n'
    for file in glob.glob("*-quiz.txt"):
        str += '- '+ file +'\n'
    str = str.replace("-quiz.txt", "")

    return str

def list_players():
    dirpath = os.getcwd()
    os.chdir(dirpath)
    str = 'List of players\n'
    for file in glob.glob("*.txt"):
        with open(file) as f:
            lines = f.readlines()
            for l in lines:
                splitted = l.split()
                n = splitted[0]
                if str.find(n)==-1:
                    str += '- '+ n +'\n'

    return str

def quiz_stats(quiz_name):
    name = quiz_name + '-log.txt'
    st = ""
    try:
        with open(name) as f:
            lines = f.readlines()
            questions = {}
            st += 'total questions placed - ' + str(len(lines)) + '\n'
            timeout = 0
            correct = 0
            incorrect = 0
            for l in lines:
                answer = l.split(":")
                if int(answer[3])==0 and int(answer[2])!=0:
                    incorrect+=1

                elif int(answer[3]) == 1:
                    correct+=1

                else:
                    timeout+=1

                if int(answer[2]) != 0:
                    if answer[1] not in questions:
                        questions[answer[1]] = [0,0,0,0]
                    questions[answer[1]][int(answer[2])-1]+=1
            st +='correct questions - ' + str(correct) + '\n' +'incorrect questions - ' + str(incorrect) + '\n' + 'timedout questions - ' + str(timeout) + '\n'
            for q in questions:
                st += 'question ' + q + ':'
                i = 0
                total = 0
                for r in questions[q]:
                    total += r
                    i += 1
                    st += str(i) + '->' + str(r) + ' || '
                st += '(total questions -> ' + str(total) + ')'
                st += '\n'
        return st

    except IOError:
        return 'Quiz not registered or hasnt been answered'


def player_stats(player_name):
        if player_name not in list_players():
            return 'player is not registered'
        dirpath = os.getcwd()
        os.chdir(dirpath)
        st = ""
        for file in glob.glob("*-log.txt"):

            with open(file) as f:
                lines = f.readlines()
                timeout = 0
                correct = 0
                incorrect = 0
                for l in lines:
                    answer = l.split(":")

                    if int(answer[2])==0 and answer[0] == player_name:
                        timeout+=1

                    if int(answer[3]) == 1 and answer[0] == player_name:
                        correct+=1

                    if int(answer[3]) == 0 and answer[0] == player_name:
                        incorrect+=1
            total = correct + incorrect + timeout

            if total != 0:
                file = file.replace('-log.txt','')
                st +='---in ' +str(file)+'---' + '\n' + 'total questions placed - ' + str(total) + '\n' + 'correct questions - ' + str(correct) + '\n' +'incorrect quastions - ' + str(incorrect) + '\n' + 'timedout questions - ' + str(timeout) + '\n'

        return st





while True:

    #receive messagem from client
    print('Waiting for instruction')
    data = client.recv(MSG_SIZE)
    request = data.decode().split()
    request_type = request[TYPE]


    if(request_type == 'QS' and len(request) == 2):
        name = request[1]
        msg = quiz_stats(name)

    elif(request_type == 'PS' and len(request) == 2):
        name = request[1]
        msg = player_stats(name)

    elif (request_type == 'LQ' and len(request) == 1):
        msg = list_quizes()

    elif (request_type == 'LP' and len(request) == 1):
        msg = list_players()

    else:
        msg = 'Invalid input'

    msg_sent = msg.encode()
    client.send(msg_sent)

server_socket.close()

    #send message to client
