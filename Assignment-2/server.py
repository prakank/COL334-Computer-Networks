import socket
import sys
import os
import select
import threading

HEADER = 64
PORT = 5051
FORMAT = 'utf-8'
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(ADDR)

list_of_clients = {}
sockets_list = {'server':server_socket}

def registration(client_socket, client_address):
    pass


def handle_client(client_socket, client_address):
    username = registration(client_socket, client_address)
    connected = True
    while connected:
        msg_length = client_socket.recv(HEADER).decode(FORMAT) # Blocking line
        if msg_length:
            msg_length = int(msg_length)
            msg = client_socket.recv(msg_length).decode(FORMAT)
        
            if msg == "DISCONNECT_MESSAGE":
                connected = False
            
            print(f"[{addr}] {msg}")
            client_socket.send("Msg received".encode(FORMAT))        
    client_socket.close()
    
        
def main():
    server_socket.listen()    
    while True:
        client_socket, client_address = server_socket.accept()   # Blocking line
        thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        thread.start()
        
    
        # print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}\n")
    # print(f"[LISTENING] Server is listening on ({SERVER}, {PORT})\n")
    # while True:
    #     readable, writable, exceptional = select.select(sockets_list, [], sockets_list)
        
    #     for readable_socket in readable:
    #         if readable_socket == server_socket:
    #             client_socket, client_address = server_socket.listen()
    #             username = registration(client_socket, client_address) #Continue till not valid
                
    #         else:
                
    
        # conn, addr = server_socket.accept()   # Blocking line
        # thread = threading.Thread(target=handle_client, args=(conn, addr))
        # thread.start()
        
if __name__ == '__main__':
    main()

# # Python program to implement server side of chat room.
# import socket
# import select
# import sys
# from _thread import *

# """The first argument AF_INET is the address domain of the
# socket. This is used when we have an Internet Domain with
# any two hosts The second argument is the type of socket.
# SOCK_STREAM means that data or characters are read in
# a continuous flow."""
# server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# # checks whether sufficient arguments have been provided
# if len(sys.argv) != 3:
#     print ("Correct usage: script, IP address, port number")
#     exit()

# # takes the first argument from command prompt as IP address
# IP_address = str(sys.argv[1])

# # takes second argument from command prompt as port number
# Port = int(sys.argv[2])

# """
# binds the server to an entered IP address and at the
# specified port number.
# The client must be aware of these parameters
# """
# server.bind((IP_address, Port))

# """
# listens for 100 active connections. This number can be
# increased as per convenience.
# """
# server.listen(100)

# list_of_clients = []

# def clientthread(conn, addr):

#     # sends a message to the client whose user object is conn
#     welcome = "Welcome to this chatroom!"
#     conn.send(welcome.encode('utf-8'))

#     while True:
#             try:
#                 message = conn.recv(2048)
#                 if message:

#                     """prints the message and address of the
#                     user who just sent the message on the server
#                     terminal"""
#                     print ("<" + addr[0] + "> " + message)

#                     # Calls broadcast function to send message to all
#                     message_to_send = "<" + addr[0] + "> " + message
#                     broadcast(message_to_send, conn)

#                 else:
#                     """message may have no content if the connection
#                     is broken, in this case we remove the connection"""
#                     remove(conn)

#             except:
#                 continue

# """Using the below function, we broadcast the message to all
# clients who's object is not the same as the one sending
# the message """
# def broadcast(message, connection):
#     for clients in list_of_clients:
#         if clients!=connection:
#             try:
#                 clients.send(message)
#             except:
#                 clients.close()

#                 # if the link is broken, we remove the client
#                 remove(clients)

# """The following function simply removes the object
# from the list that was created at the beginning of
# the program"""
# def remove(connection):
#     if connection in list_of_clients:
#         list_of_clients.remove(connection)

# while True:

#     """Accepts a connection request and stores two parameters,
#     conn which is a socket object for that user, and addr
#     which contains the IP address of the client that just
#     connected"""
#     conn, addr = server.accept()

#     """Maintains a list of clients for ease of broadcasting
#     a message to all available people in the chatroom"""
#     list_of_clients.append(conn)

#     # prints the address of the user that just connected
#     print (addr[0] + " connected")

#     # creates and individual thread for every user
#     # that connects
#     start_new_thread(clientthread,(conn,addr))	

# conn.close()
# server.close()
