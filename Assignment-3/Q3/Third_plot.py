import os
import matplotlib.pyplot as plt
import sys
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

configuration = [1, 2, 3]
tcp_connection_num = [1, 2, 3]

def graph_plot(filepath,c,t,x,y,dropped):
    file = os.path.join(filepath,'q3_{}_{}_plot.png'.format(c,t))
    plt.plot(x,y)
    plt.title("Congestion Window Size vs Time (Configuration:{}, TcpSocket:{}, Dropped:{})".format(c,t,dropped), fontsize=8)
    plt.xlabel('Time (sec)', fontsize=8)
    plt.ylabel('Congestion Window',fontsize=8)
    x_axis = [0, 5, 10, 15, 20, 25, 30]
    plt.xticks(x_axis)
    plt.savefig(file)
    plt.show()    

for c in configuration:
    for t in tcp_connection_num:
        file = ("q3_{}_{}.cwnd".format(c,t))
        filepath_part = os.path.join(BASE_DIR, 'Q3', 'output3')
        filepath = os.path.join(BASE_DIR, 'Q3', 'output3', file)
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
            
        graph_plot(filepath_part,c,t,x,y,dropped)
    
