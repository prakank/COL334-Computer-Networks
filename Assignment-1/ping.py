import os

hostname = "www.youtube.com"

START = {"www.facebook.com":1471, "www.google.com":67, "www.iitd.ac.in":1471, "www.codeforces.com":1471, "www.youtube.com":67}
# Storing the max_size-1 in START so as to minimize the number of ping commnads for the next time
# Storing max_size-1 so as to make sure that the max_size value is attained

MAX_SIZE     = 1000000
TTL_MAX_SIZE = 255

threshold_pack_size = 1
threshold_ttl       = 1

CLEAR = True

def packet_size(List):
    max_pack_size = {}
    for hostname in List:
        print(hostname) 
        Start_check = os.system("ping -c 1 {}".format(hostname))
        if Start_check == 0:
            for max_size in range(START[hostname],MAX_SIZE):
                count = 0
                while count < threshold_pack_size:
                    response = os.system("ping -s {} -c 1 {}".format(max_size, hostname))
                    if response == 0:
                        break
                    else:
                        count+=1
                if count == threshold_pack_size:
                    print("Max packet size for {}: {}".format(hostname, max_size-1))
                    max_pack_size[hostname] = max_size-1
                    break
                elif CLEAR:
                    os.system('clear')
        else:
            print("{} is down!".format(hostname))
    return max_pack_size        
            
def ttl_values(List):
    min_ttl = {}
    for hostname in List:
        print(hostname) 
        Start_check = os.system("ping -c 1 {}".format(hostname))
        if Start_check == 0:
            for ttl in range(1,TTL_MAX_SIZE+1):
                count = 0
                while count < threshold_ttl:
                    response = os.system("ping -t {} -c 1 {}".format(ttl, hostname))
                    if response == 0:
                        print("Minimum ttl for {}: {}".format(hostname, ttl))
                        min_ttl[hostname] = ttl
                        break
                    else:
                        count+=1
                if count < threshold_ttl:
                    break
                elif CLEAR:
                    os.system('clear')
        else:
            print("{} is down!".format(hostname))
    return min_ttl

if __name__ == '__main__':
    sites = ["www.google.com", "www.facebook.com", "www.iitd.ac.in"]
    L1 = packet_size(sites)
    L2 = ttl_values(sites)
    print("Max. packet size:",L1)
    print("Min. ttl values:",L2)