import socket
import threading
from _thread import *
import sys
import re

FORMAT = 'utf-8'
HEADER_LENGTH = 200

def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH).decode(FORMAT)
        return message_header
        # print(message_header, len(message_header))
        # if len(message_header):
        #     message_length = int(message_header.decode(FORMAT))
        #     return client_socket.recv(message_length).decode(FORMAT)    
    except:
        print(sys.exc_info[0])
        raise Exception("")

# def send_message(message, client_socket):
#     try:
#         client_socket.send()
    
class TCP_Server:
    
    sendSocket_list = {}
    recvSocket_list = {}    #static
    
    def __init__(self, host, port):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((host, port))
        except socket.error as err:
            raise IOError('Unable to bind receiver socket: {}'.format(err))                
        self.start()
        
    
    def start(self):
        self.server_socket.listen()
        i = 0
        while True:
            print("Value" + str(i))
            client_socket, client_address = self.server_socket.accept()
            i+=1
            client_handler = Handle_Client(client_socket)
            thread10 = threading.Thread(target=client_handler.run)
            thread10.start()


class Handle_Client:
    def __init__(self, client_socket):
        self.client_socket   = client_socket        
        self.username        = ""
        
    def run(self):
        username_pattern = re.compile(r"^[A-Za-z0-9]+$")
        
        while True:
            line = receive_message(self.client_socket)
            if line.split(" ")[0] == "REGISTER" and line.split(" ")[1] == "TOSEND":
                username = (line.split(" ",2)[2]).split("\n")[0]
                print(username)
                if bool(re.match(username_pattern, username)):
                    self.client_socket.send(("REGISTERED TOSEND " + username + '\n \n').encode(FORMAT))
                    self.username = username
                    TCP_Server.sendSocket_list[username] = self.client_socket
                    self.conversation_begin()
                    return
                else:
                    self.client_socket.send(("ERROR 100 Malformed username\n \n").encode(FORMAT))
                    continue
                
            elif line.split(" ")[0] == "REGISTER" and line.split(" ")[1] == "TORECV":
                username = line.split(" ",2)[2]
                if username in TCP_Server.sendSocket_list.keys():
                    self.client_socket.send(("REGISTERED TORECV " + username + '\n \n').encode(FORMAT))
                    self.username = username
                    TCP_Server.recvSocket_list[username] = self.client_socket
                    return
                
                elif not bool(re.match(username_pattern, username)):
                    self.client_socket.send(("ERROR 100 Malformed username\n \n").encode(FORMAT))
                else:
                    self.client_socket.send(("ERROR 101 No user registered \n \n").encode(FORMAT))
            
            else:
                self.client_socket.send(("ERROR 101 No user registered \n \n").encode(FORMAT))
    
    def conversation_begin(self):
        sender_pattern         = re.compile(r"^SEND\s[A-Za-z0-9]+$")
        content_length_pattern = re.compile(r"^Content-length:\s[0-9]+$")
        while True:
            line = receive_message(self.client_socket)            
            if(line.split(" ")[0] == "SEND"):
                if len(line.split("\n",3))!=4:
                    self.client_socket.send(("ERROR 103 Header incomplete\n\n"))
                    continue
                sender_line  = line.split("\n")[0]
                content_line = line.split("\n")[1]
                if bool(re.match(sender_pattern,sender_line)) and bool(re.match(content_length_pattern, content_line)):
                    recipient      = sender_line.split(" ")[1]
                    content_length = int(content_line.split(" ")[1])
                    message = line.split("\n",3)[-1]
                    message = message[:content_length]
                    if recipient in TCP_Server.recvSocket_list.keys():
                        try:
                            TCP_Server.recvSocket_list[recipient].send(("FORWARD " + self.username + "\nContent-length: " + str(content_length) + "\n\n" + message).encode(FORMAT))
                            response = receive_message(TCP_Server.recvSocket_list[recipient])
                            expected = "RECEIVED " + self.username + "\n\n"
                            if response == expected:
                                self.client_socket.send(("SEND " + self.username + "\n\n"))
                            else:
                                self.client_socket.send(("ERROR 102 Unable to send\n\n").encode(FORMAT))
                                
                        except:
                            self.client_socket.send(("ERROR 102 Unable to send\n\n").encode(FORMAT))
                    else:
                        self.client_socket.send(("ERROR 102 Unable to send\n\n").encode(FORMAT))
                                        
            # elif (line.split(" ")[0] == "RECEIVED"):
            #     sender_username = (line.split(" ")[1]).split("\n")[0]
            #     TCP_Server.recvSocket_list[sender_username].send(("SEND " + self.username + "\n\n").encode(FORMAT))
                
            else:
                self.client_socket.send(("ERROR 103 Header incomplete\n\n"))
                
        
if __name__ =="__main__":
    host = "127.0.0.1"
    port = 10000
    server = TCP_Server(host, port)
    
    port_pattern = re.compile(r"^[0-9]+$")
    ip_pattern = re.compile(r"^[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}$")
    
    # if len(sys.argv) != 3:
    #     raise IOError('Incorrect arguments')
    # else:
    #     if (len(sys.argv[1]) == 'localhost' or bool(re.match(ip_pattern, sys.argv[1])) ) and bool(re.match(port_pattern, sys.argv[2])):
    #         client = TCP_Client(sys.argv[1], sys.argv[2])
    #     else:
    #         raise IOError('Incorrect arguments')
            
    