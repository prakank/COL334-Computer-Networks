import socket
import threading
from _thread import *
import sys
import re
import argparse

FORMAT = 'utf-8'
HEADER_LENGTH = 1024

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
    
class TCP_Server:
    
    sendSocket_list = {}
    recvSocket_list = {}    #static
    
    def __init__(self, host, port, max_clients):
        try:
            if host == "localhost":
                host = "127.0.0.1"
            
            self.host = host
            self.port = port
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.max_clients = max_clients
            
        except socket.error as err:
            raise IOError('Unable to bind receiver socket: {}'.format(err))
        
        
        self.start()
        
    
    def start(self):
        print("Server Running on HOST: {} and PORT: {}".format(self.host, self.port))
        print("Waiting for Connection ...\n")
        self.server_socket.listen()
        
        while True:
            while len(TCP_Server.recvSocket_list) < self.max_clients:
                client_socket, client_address = self.server_socket.accept()
                client_handler = Handle_Client(client_socket)
                thread10 = threading.Thread(target=client_handler.run)
                thread10.start()
            
        # if len(TCP_Server.recvSocket_list) == self.max_clients:
        #     print("\nMax Limit Reached ...")
            


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
                
                if bool(re.match(username_pattern, username)) and (username not in TCP_Server.sendSocket_list.keys()) and username != "ALL":
                    self.client_socket.send(("REGISTERED TOSEND " + username + '\n \n').encode(FORMAT))
                    self.username = username
                    TCP_Server.sendSocket_list[username] = self.client_socket
                    self.conversation_begin()
                    return
                else:
                    self.client_socket.send(("ERROR 100 Malformed username\n \n").encode(FORMAT))
                    continue
                
            elif line.split(" ")[0] == "REGISTER" and line.split(" ")[1] == "TORECV":
                username = (line.split(" ",2)[2]).split("\n")[0]
                
                if username in TCP_Server.sendSocket_list.keys():
                    self.client_socket.send(("REGISTERED TORECV " + username + '\n \n').encode(FORMAT))
                    self.username = username
                    TCP_Server.recvSocket_list[username] = self.client_socket
                    print(username + " entered the chatroom!")
                    return
                
                elif not bool(re.match(username_pattern, username)):
                    self.client_socket.send(("ERROR 100 Malformed username\n \n").encode(FORMAT))
                
                else:
                    self.client_socket.send(("ERROR 101 No user registered \n \n").encode(FORMAT))
            
            else:
                self.client_socket.send(("ERROR 101 No user registered \n \n").encode(FORMAT))
    
    def conversation_begin(self):
        sender_pattern          = re.compile(r"^SEND\s[A-Za-z0-9]+$")
        content_length_pattern  = re.compile(r"^Content-length:\s[0-9]+$")
        registered_successfully = False
        
        while True:
            line = receive_message(self.client_socket)
            
            if not registered_successfully and (self.username not in TCP_Server.sendSocket_list.keys() or self.username not in TCP_Server.recvSocket_list.keys()):
                self.client_socket.send(("ERROR 101 No user registered \n \n").encode(FORMAT))
                continue
            else:
                registered_successfully = True
            
            if(line.split(" ")[0] == "SEND"):
                
                if len(line.split("\n",3))!=4:
                    self.client_socket.send(("ERROR 103 Header incomplete\n\n").encode(FORMAT))
                    TCP_Server.recvSocket_list[self.username].send(("ERROR 103 Header incomplete\n\n").encode(FORMAT))
                    
                    TCP_Server.sendSocket_list.pop(self.username,None)
                    TCP_Server.recvSocket_list.pop(self.username,None)
                    return #Close the socket

                sender_line  = line.split("\n")[0]
                content_line = line.split("\n")[1]
            
                if (bool(re.match(sender_pattern,sender_line)) or sender_line == "ALL")  and bool(re.match(content_length_pattern, content_line)):
                    recipient      = sender_line.split(" ")[1]
                    content_length = int(content_line.split(" ")[1])
                    message = line.split("\n",3)[-1]
                    
                    if(len(message) != content_length):
                        self.client_socket.send(("ERROR 103 Header incomplete\n\n").encode(FORMAT))
                        TCP_Server.recvSocket_list[self.username].send(("ERROR 103 Header incomplete\n\n").encode(FORMAT)) #For closing both sockets at Client side
                        
                        TCP_Server.sendSocket_list.pop(self.username,None)
                        TCP_Server.recvSocket_list.pop(self.username,None) #client's connection closed
                        return #Close the socket
                                        
                    if recipient in TCP_Server.recvSocket_list.keys():            
                        try:
                            TCP_Server.recvSocket_list[recipient].send(("FORWARD " + self.username + "\nContent-length: " + str(content_length) + "\n\n" + message).encode(FORMAT))
                            response = receive_message(TCP_Server.recvSocket_list[recipient])
                            expected_recv = "RECEIVED " + self.username + "\n\n"

                            if response == expected_recv:
                                self.client_socket.send(("SEND " + recipient + "\n\n").encode(FORMAT))
                            
                            elif response == "ERROR 103 Header Incomplete\n\n":
                                self.client_socket.send(("ERROR 102 Unable to send\n\n").encode(FORMAT))
                                TCP_Server.sendSocket_list[recipient].send(("ERROR 103 Header incomplete\n\n").encode(FORMAT))
                                TCP_Server.recvSocket_list[recipient].send(("ERROR 103 Header incomplete\n\n").encode(FORMAT))                                

                                TCP_Server.sendSocket_list.pop(recipient,None)
                                TCP_Server.recvSocket_list.pop(recipient,None) #recipient's connection closed
                            
                            else:
                                self.client_socket.send(("ERROR 102 Unable to send\n\n").encode(FORMAT))
                                
                        except:
                            self.client_socket.send(("ERROR 102 Unable to send\n\n").encode(FORMAT))
                    
                    elif recipient == "ALL":
                        break_condition = False
                        
                        for recipient in TCP_Server.recvSocket_list.keys():
                            
                            if recipient == self.username:
                                continue                            
                            
                            TCP_Server.recvSocket_list[recipient].send(("FORWARD " + self.username + "\nContent-length: " + str(content_length) + "\n\n" + message).encode(FORMAT))
                            response = receive_message(TCP_Server.recvSocket_list[recipient])
                            expected_recv = "RECEIVED " + self.username + "\n\n"
                            
                            if response == "ERROR 103 Header Incomplete\n\n":
                                print(recipient, "INCOMPLETE")
                                TCP_Server.sendSocket_list[recipient].send(("ERROR 103 Header incomplete\n\n").encode(FORMAT))
                                TCP_Server.recvSocket_list[recipient].send(("ERROR 103 Header incomplete\n\n").encode(FORMAT))                                

                                TCP_Server.sendSocket_list.pop(recipient,None)
                                TCP_Server.recvSocket_list.pop(recipient,None) #recipient's connection closed
                                break_condition = True
                                break

                            elif response != expected_recv:                                
                                break_condition = True
                                break
                                
                        if not break_condition:
                            self.client_socket.send(("SEND ALL\n\n").encode(FORMAT))
                            print("\nBroadcast message by " + self.username)
                        else:
                            self.client_socket.send(("ERROR 102 Unable to send to ALL\n\n").encode(FORMAT))
                                                                                    
                        recipient = "ALL"
                        
                    else:
                        self.client_socket.send(("ERROR 102 Unable to send\n\n").encode(FORMAT))

                # elif bool(re.match(sender_pattern,sender_line)) and not bool(re.match(content_length_pattern, content_line)):
                #     self.client_socket.send(("ERROR 103 Header incomplete\n\n").encode(FORMAT))
                #     TCP_Server.recvSocket_list[self.username].send(("ERROR 103 Header incomplete\n\n").encode(FORMAT))
                    
                #     TCP_Server.sendSocket_list.pop(self.username,None)
                #     TCP_Server.recvSocket_list.pop(self.username,None)
                #     return #Close the socket

                else:
                    self.client_socket.send(("ERROR 103 Header incomplete\n\n").encode(FORMAT))
                    TCP_Server.recvSocket_list[self.username].send(("ERROR 103 Header incomplete\n\n").encode(FORMAT))
                    
                    TCP_Server.sendSocket_list.pop(self.username,None)
                    TCP_Server.recvSocket_list.pop(self.username,None)
                    return #Close the socket
            
            else:
                self.client_socket.send(("ERROR 103 Header incomplete\n\n").encode(FORMAT))
                TCP_Server.recvSocket_list[self.username].send(("ERROR 103 Header incomplete\n\n").encode(FORMAT))
                
                TCP_Server.sendSocket_list.pop(self.username,None)
                TCP_Server.recvSocket_list.pop(self.username,None)
                return #Close the socket
                
        
if __name__ =="__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", type=int,default=10,help="Maximum Number of Connections")
    parser.add_argument("-ip", type=str,default="127.0.0.1",help="IP address")
    parser.add_argument("-p", type=int,default=10000,help="PORT")
    opt = parser.parse_args()
    
    max_clients = int(opt.n)
    host = str(opt.ip)
    port = int(opt.p)
    
    server = TCP_Server(host, port, max_clients)
    
    port_pattern = re.compile(r"^[0-9]+$")
    ip_pattern = re.compile(r"^[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}$")
    
    # if len(sys.argv) != 3:
    #     raise IOError('Incorrect arguments')
    # else:
    #     if (len(sys.argv[1]) == 'localhost' or bool(re.match(ip_pattern, sys.argv[1])) ) and bool(re.match(port_pattern, sys.argv[2])):
    #         client = TCP_Client(sys.argv[1], sys.argv[2])
    #     else:
    #         raise IOError('Incorrect arguments')
