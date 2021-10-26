import os
import matplotlib.pyplot as plt
import sys
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cdr_list = [2, 4, 10, 20, 50]
adr_list = [0.5, 1, 2, 4, 10]

def graph_plot(filepath,cdr,adr,x,y,dropped):
    file = os.path.join(filepath,'q2_cdr_' + str(cdr) + "Mbps_adr_" + str(adr) + 'Mbps_plot.png')
    plt.plot(x,y)
    plt.title("Congestion Window Size vs Time (CDR:{}, ADR:{}, Dropped:{})".format(cdr,adr,dropped), fontsize=8)
    plt.xlabel('Time (sec)', fontsize=8)
    plt.ylabel('Congestion Window', fontsize=8)
    plt.savefig(file)
    # if protocol == 'Vegas':
    plt.show()    


for cdr in cdr_list:
    adr = 2
    file = ("q2_cdr_{}Mbps_adr_{}Mbps.cwnd".format(cdr,adr))
    filepath_part = os.path.join(BASE_DIR, 'Q2', 'output2')
    filepath = os.path.join(BASE_DIR, 'Q2', 'output2', file)
    file_data = open(filepath).readlines()
    x,y = [],[]
    dropped = 0
    
    for lines in file_data:
        line = lines[0:len(lines)-1].split('\t')
        line[0] = float(line[0])
        line[1] = int(line[1])

        initial_size = line[1]
        final_size = int(line[2])

        if (final_size < initial_size):
            dropped+=1

        x.append(line[0])
        y.append(line[1])
    graph_plot(filepath_part,cdr,adr,x,y,dropped)
    

for adr in adr_list:
    cdr = 6
    file = ("q2_cdr_{}Mbps_adr_{}Mbps.cwnd".format(cdr,adr))
    filepath_part = os.path.join(BASE_DIR, 'Q2', 'output2')
    filepath = os.path.join(BASE_DIR, 'Q2', 'output2', file)
    file_data = open(filepath).readlines()
    x,y = [],[]
    dropped = 0
    
    for lines in file_data:
        line = lines[0:len(lines)-1].split('\t')
        line[0] = float(line[0])
        line[1] = int(line[1])

        initial_size = line[1]
        final_size = int(line[2])

        if (final_size < initial_size):
            dropped+=1

        x.append(line[0])
        y.append(line[1])
    graph_plot(filepath_part,cdr,adr,x,y,dropped)



# for protocol in Protocol:
#     file = 'q2_' + protocol + '.cwnd'
#     filepath_part = os.path.join(BASE_DIR, 'Q2', 'output2')
#     filepath = os.path.join(BASE_DIR, 'Q2', 'output2', file)
    
#     file_data = open(filepath).readlines()
#     x,y = [],[]
#     drop_data = []
    
#     dropped = 0
#     for lines in file_data:
#         line = lines[0:len(lines)-1].split('\t')
#         line[0] = float(line[0])
#         line[1] = int(line[1])
        
#         initial_size = line[1]
#         final_size = int(line[2])
        
#         if (final_size < initial_size):
#             dropped+=1
        
#         x.append(line[0])
#         y.append(line[1])
#     graph_plot(filepath_part,protocol,x,y,dropped)
    
#     # break