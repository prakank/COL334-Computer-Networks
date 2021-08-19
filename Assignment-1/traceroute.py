# references:
#   https://blogs.oracle.com/ksplice/entry/learning_by_doing_writing_your

import sys
import socket
import time
import matplotlib.pyplot as plt

MAX_HOPS = 64
# HOST = socket.gethostbyname(socket.gethostname())
HOST = ''

def traceroute(dest_addr, max_hops=MAX_HOPS, timeout=0.2):
    proto_icmp = socket.getprotobyname('icmp')
    proto_udp = socket.getprotobyname('udp')
    port = 33434

    for ttl in range(1, max_hops+1):
        initial_time = time.time()
        rx = socket.socket(socket.AF_INET, socket.SOCK_RAW, proto_icmp)
        rx.settimeout(timeout)
        rx.bind((HOST, port))
        
        tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto_udp)
        tx.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
        tx.sendto(b'Hello', (dest_addr, port))
        

        try:
            ending_time = time.time()
            elapsed_time = str((ending_time - initial_time)*100000)[:4] + "ms"
            data, curr_addr = rx.recvfrom(512)
            # print(curr_addr, type(curr_addr))
            curr_addr = curr_addr[0]
        except socket.error:
            curr_addr = "Request timed out"
            elapsed_time = "  *  "
        finally:
            rx.close()
            tx.close()

        yield (curr_addr, elapsed_time) # yield is a keyword that returns from the function without destroying the state of it's local variables.

        if curr_addr == dest_addr:
            break

def graph(data, dest_name, dest_addr):
    plt.plot(data)
    plt.title(dest_name + " (" + dest_addr + ")")
    plt.savefig("output.jpg")
    plt.show()    

if __name__ == "__main__":
    dest_name = sys.argv[1]
    # dest_name = "www.google.com"
    dest_addr = socket.gethostbyname(dest_name)
    print("traceroute to {} ({}), {} hops max".format(dest_name, dest_addr, MAX_HOPS))
    
    data = []
    
    for i, v in enumerate(traceroute(dest_addr)):
        print("{}\t{}\t\t{}".format(i+1, v[1], v[0]))
        if(v[1] == "  *  "):
            data.append(0)
        else:
            data.append(float(v[1][:len(v[1])-2]))
    graph(data, dest_name, dest_addr)