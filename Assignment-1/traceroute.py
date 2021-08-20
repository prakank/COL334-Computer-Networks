# references:
#   https://blogs.oracle.com/ksplice/entry/learning_by_doing_writing_your

import sys
import socket
import time
import matplotlib.pyplot as plt

MAX_HOPS = 15
TIMEOUT = 0.4
HOST = ''
# HOST = socket.gethostbyname(socket.gethostname())

def tr(host_addr, max_hops = MAX_HOPS, timeout = TIMEOUT):
    
    icmp = socket.getprotobyname('icmp')
    udp = socket.getprotobyname('udp')
    PORT = 5000

    for ttl in range(1, max_hops+1):
        initial_time = time.time()
        receive = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
        receive.settimeout(timeout)
        receive.bind((HOST, PORT))
        
        transmit = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, udp)
        transmit.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
        transmit.sendto(b'Hello World!', (host_addr, PORT))

        try:
            ending_time = time.time()
            elapsed_time = str((ending_time - initial_time)*100000)[:4] + "ms"
            _, curr_addr = receive.recvfrom(512)
            curr_addr = curr_addr[0]
        except socket.error:
            curr_addr = "Request timed out"
            elapsed_time = "  *  "
        finally:
            receive.close()
            transmit.close()

        yield (curr_addr, elapsed_time) # yield is a keyword that returns from the function without destroying the state of it's local variables.

        if curr_addr == host_addr:
            return

def graph(data, dest_name, dest_addr):
    plt.plot(data)
    plt.title(dest_name + " (" + dest_addr + ")")
    plt.xlabel("Hops")
    plt.ylabel("Round Trip Time (RTT) (ms)")
    plt.savefig("output.jpg")
    plt.show()    

if __name__ == "__main__":
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
                        
    print("\ntraceroute to {} ({}), {} hops max".format(hostname, host_addr, MAX_HOPS))
    
    data = []
    
    for i, tup in enumerate(tr(host_addr)):
        print("{}\t{}\t\t{}".format(i+1, tup[0], tup[1]))
        if(tup[1] == "  *  "):
            data.append(0)
        else:
            data.append(float(tup[1][:len(tup[1])-2]))
    graph(data, hostname, host_addr)