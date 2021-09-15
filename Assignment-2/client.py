import socket
import threading
from _thread import *
import sys, os
import re

FORMAT = 'utf-8'
HEADER_LENGTH = 20

class client_sender:
    def __init__(self, username, sendSocket):
        self.username = username
        self.sendSocket = sendSocket
    
    def run(self): # waiting for client to type in
        try:            
            while True:
                line = input("You: ")
                if(line[0] == '@'):
                    line = line.split(" ", 1)
                    recipient = line[0][1:]
                    message  = line[1]
                else:
                    print("Incorrect Format (Use @ to mention the receipient")
                    continue
                
                self.sendSocket.send(("SEND " + recipient + "\nContent-length: " + len(message) + "\n\n" + message).encode(FORMAT))
                respone_header = self.sendSocket.recv(HEADER_LENGTH)
                
                if respone_header:
                    respone_header = int(respone_header.decode(FORMAT))
                    respone = self.sendSocket.recv(respone_header).decode(FORMAT)
                    if respone.split(" ")[0] == "SEND":
                        print("Message delivered successfully")
                    elif respone.split(" ")[1] == "102":
                        print("ERROR 102 Unable to send (Recipient not registered)")
                    elif respone.split(" ")[1] == "103":
                        print("ERROR 103 Header Incomplete")            
        except:
            print(sys.exc_info[0])
            raise Exception("")
        
class client_receiver:
    def __init__(self, username, recvSocket):
        self.username = username
        self.recvSocket = recvSocket
    
    def run(self):
        while True:
            header = self.recvSocket.recv(HEADER_LENGTH)
            if header:
                header = int(header.decode(FORMAT))
                line = self.recvSocket.recv(header).decode(FORMAT)
                line = line.split("\n",3)
                
                #DEBUG
                #Look for this lines in case of error (\s)
                
                sender_pattern         = re.compile(r"FORWARD\s[A-Za-z0-9_]+")
                content_length_pattern = re.compile(r"Content-length:\s[0-9]+")
                
                sender         = line[0]
                content_length = line[1]
                message        = line[3]
                
                if bool(re.match(sender_pattern, sender)) and bool(re.match(content_length_pattern, content_length)):
                    sender = line[0].split(" ")[1]
                    content_length = line[1].split(" ")[1]
                    print(sender + ": " + message)
                    self.recvSocket.send(("RECEIVED " + sender).encode(FORMAT))
                else:
                    self.recvSocket.send(("ERROR 103 Header Incomplete\n\n").encode(FORMAT))

class TCP_Client:
    def __init__(self, host, port):
        try:
            self.sendSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sendSocket.connect((host, port))
            self.recvSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.recvSocket.connect((host, port))            
        except socket.error as err:
            raise IOError('Unable to bind receiver socket: {}'.format(err))

        self.registration()
        print("--------------------------------Connected to the chatroom--------------------------------")
        
        clientSender = client_sender(self.username, self.sendSocket)
        thread2 = threading.Thread(target=clientSender.run())
        thread2.start()
        
        clientReceiver = client_receiver(self.username, self.recvSocket)
        thread3 = threading.Thread(target=clientReceiver.run())
        thread3.start()

    def registration(self):
        self.send_registration() #We have a valid Username
        self.recv_registration()
        
    def send_registration(self):
        while True:
            self.username = input('Username: ')
            self.sendSocket.send(('REGISTER TOSEND ' + self.username).encode(FORMAT))            
            message_header = self.sendSocket.recv(HEADER_LENGTH)
            if message_header:
                message_header = int(message_header.decode(FORMAT))
                response = self.sendSocket.recv(message_header).decode(FORMAT)
                if response.split(" ")[0] == "REGISTERED":
                    print("\nREGISTERED TOSEND " + self.username)
                    return
                else:
                    print("Invalid username (Can contain only A-Z, a-z, 0-9 chars) or Username already registered")

    def recv_registration(self):
        self.recvSocket.send(('REGISTER TORECV ' + self.username).encode(FORMAT))
        message_header = self.recvSocket.recv(HEADER_LENGTH)
        if message_header:
            message_header = int(message_header.decode(FORMAT).strip())
            response = self.recvSocket.recv(message_header).decode(FORMAT)
            if response.split(" ")[0] == "REGISTERED":
                print("REGISTERED TORECV " + self.username)
                return
        
                                   
if __name__ == '__main__':
    host = "127.0.0.1"
    port = 10000
    client = TCP_Client(host, port)
    
    port_pattern = re.compile(r"[0-9]+")
    ip_pattern = re.compile(r"[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}")
    
    # if len(sys.argv) != 3:
    #     raise IOError('Incorrect arguments')
    # else:
    #     if (len(sys.argv[1]) == 'localhost' or bool(re.match(ip_pattern, sys.argv[1])) ) and bool(re.match(port_pattern, sys.argv[2])):
    #         client = TCP_Client(sys.argv[1], sys.argv[2])
    #     else:
    #         raise IOError('Incorrect arguments')
            
    