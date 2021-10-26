import os
import matplotlib.pyplot as plt
import sys
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Protocol = ['NewReno', 'HighSpeed', 'Veno', 'Vegas']

def graph_plot(filepath,protocol,x,y,dropped):
    file = os.path.join(filepath,'q1_' + protocol + '_plot.png')
    plt.plot(x,y)
    plt.title(protocol + " (Dropped Packets: {})".format(dropped))
    plt.xlabel('Time (sec)')
    plt.ylabel('Congestion Window')
    plt.savefig(file)
    # if protocol == 'Vegas':
    plt.show()    

for protocol in Protocol:
    file = 'q1_' + protocol + '.cwnd'
    filepath_part = os.path.join(BASE_DIR, 'Q1', 'output1')
    filepath = os.path.join(BASE_DIR, 'Q1', 'output1', file)
    
    file_data = open(filepath).readlines()
    x,y = [],[]
    drop_data = []
    
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
    graph_plot(filepath_part,protocol,x,y,dropped)
    
    # break