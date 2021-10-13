import os
import matplotlib.pyplot as plt
import sys
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Protocol = ['NewReno', 'HighSpeed', 'Veno', 'Vegas']

def graph_plot(filepath,protocol,x,y):
    file = os.path.join(filepath,'q1_' + protocol + '_plot.png')
    plt.plot(x,y)
    plt.title(protocol)
    plt.xlabel('Time')
    plt.ylabel('Congestion Window')
    plt.savefig(file)
    # if protocol == 'Vegas':
    plt.show()    

for protocol in Protocol:
    file = 'q1_' + protocol + '.txt'
    filepath_part = os.path.join(BASE_DIR,'output')
    filepath = os.path.join(BASE_DIR,'output',file)
    
    file_data = open(filepath).readlines()
    x,y = [],[]
    drop_data = []
    
    for lines in file_data:
        if lines[0:6] == "RxDrop":
            drop_data.append(lines)
        else:
            line = lines[0:len(lines)-1].split('\t')
            line[0] = float(line[0])
            line[1] = int(line[1])
            x.append(line[0])
            y.append(line[1])
    graph_plot(filepath_part,protocol,x,y)
    # break