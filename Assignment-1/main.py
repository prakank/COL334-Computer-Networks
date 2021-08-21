# Prakhar Aggarwal
# 2019CS50441

import socket
import sys
import struct
import time
import matplotlib.pyplot as plt
import numpy as np

MAX_HOPS = 60
PORT = 33434
HOST = ''
Timeout_msg = "Request timed out"

def domain_input():
    hostname = ""
    found = False
    
    try:
        hostname = sys.argv[1]
    except:        
        while hostname == "":
            print("Hostname:",end="")
            hostname = input()
    
    while found == False:
        try:
            host_addr = socket.gethostbyname(hostname)
            found = True
        except:
            print("Incorrect hostname")
            print("Hostname:",end="")
            hostname = input()
            while hostname == "":
                print("Hostname:",end="")
                hostname = input()
    
    return (hostname,host_addr)

class Traceroute():
    def __init__(self, hostname, host_addr):
        self.hostname  = hostname
        self.host_addr = host_addr
        self.port = PORT
        self.hops = MAX_HOPS
        self.ttl  = 1
        self.data = [0]
        
    def graph(self):        
        y = np.arange(0,self.ttl+1)
        
        plt.plot(self.data)
        plt.title(self.hostname + " (" + self.host_addr + ")")
        plt.xlabel("Hops")
        plt.ylabel("Round Trip Time (RTT) (ms)")
        plt.xticks(y)
        for i in range(1,len(y)):
            plt.annotate(i, (y[i],self.data[i] + 0.4))
        plt.savefig("output_line.jpg")
        plt.show()
        
        plt.title(self.hostname + " (" + self.host_addr + ")")
        plt.xlabel("Hops")
        plt.ylabel("Round Trip Time (RTT) (ms)")
        plt.xticks(y)
        plt.scatter(y,self.data)
        for i in range(len(y)):
            plt.annotate(i+1, (y[i],self.data[i] + 0.4))
        plt.savefig("output_scatter.jpg")
        plt.show()
    
    def init_receiver(self):
        
        seconds = 1
        microseconds = 0
        proto_icmp = socket.getprotobyname('icmp')
        receive = socket.socket(socket.AF_INET, socket.SOCK_RAW, proto_icmp)
        
        timeval = struct.pack("ll", seconds, microseconds) 
        # conversion between Python values and C structs represented as Python bytes objects
        # Here ll stands for long long
                        
        receive.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeval)
        # level
            # The level argument specifies the protocol level at which the option resides. 
            # To set options at the socket level, specify the level argument as SOL_SOCKET. 
            # SOL_SOCKET is the socket layer itself. It is used for options that are protocol independent.
        
        # option name
            # SO_RCVTIMEO
            # Sets the timeout value that specifies the maximum amount of time an input function waits until it completes. 
            # It accepts a timeval structure with the number of seconds and microseconds (struct.pack)
            # specifying the limit on how long to wait for an input operation to complete. 
        
        try:
            receive.bind((HOST,self.port))
            
        except socket.error as err:
            raise IOError('Unable to bind receiver socket: {}'.format(err))

        return receive
    
    def init_transmitter(self):        
        proto_udp   = socket.getprotobyname('udp')
        transmitter = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto_udp)
        transmitter.setsockopt(socket.SOL_IP, socket.IP_TTL, self.ttl)        
        return transmitter
    
    def start(self):
        print("traceroute to {} ({}), {} hops max".format(self.hostname, self.host_addr, self.hops))
        while True:
            initial_time = time.time()
            receiver     = self.init_receiver()
            transmitter  = self.init_transmitter()
            transmitter.sendto(b'', (self.host_addr, self.port))
            
            try:            
                _, curr_addr = receiver.recvfrom(512)
                ending_time = time.time()
                elapsed_time = str(round((ending_time - initial_time)*1000,3)) + " ms"
                curr_addr = curr_addr[0]                
            except socket.error as err:
                curr_addr = Timeout_msg
                elapsed_time = "  *"            
            finally:
                receiver.close()
                transmitter.close()
            
            print("{}\t{:<30}{}".format(self.ttl, curr_addr, elapsed_time))
            # print('{:<10} *'.format(self.ttl))
            
            if curr_addr != Timeout_msg:                
                self.data.append(float(elapsed_time[:len(elapsed_time)-3]))
            else:
                self.data.append(0)
            
            if curr_addr == self.host_addr:
                self.graph()
                return
            else:
                self.ttl += 1
                
            if self.ttl > self.hops:
                self.graph()
                return                
        
if __name__ == "__main__":
    hostname, host_addr = domain_input()
    tr = Traceroute(hostname=hostname, host_addr=host_addr)
    tr.start()

# Reference from this page url='https://github.com/dnaeon/pytraceroute'