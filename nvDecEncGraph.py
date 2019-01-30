#!/usr/bin/python
# MIT License
import sys
import os
import numpy as np
import subprocess
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque

# On the Jetson TX1 this is a symbolic link to:
# gpuLoadFile="/sys/devices/platform/host1x/57000000.gpu/load"
# On the Jetson TX2, this is a symbolic link to:
# gpuLoadFile="/sys/devices/platform/host1x/17000000.gp10b/load"

figDec,decAx = plt.subplots()

figDec.set_facecolor('#F2F1F0')
figDec.canvas.set_window_title('NVDEC Activity Monitor')

# For the comparison
decLine, = decAx.plot([],[])

# The line points in x,y list form
cpuy_list = deque([0]*240)
cpux_list = deque(np.linspace(60,0,num=240))

fill_lines_cpu=0

def initDecGraph():
    global decAx
    global decLine
    global fill_lines_cpu

    decAx.set_xlim(60, 0)
    decAx.set_ylim(-5, 105)
    decAx.set_title('NVDEC History')
    decAx.set_ylabel('NVDEC Usage (%)')
    decAx.set_xlabel('Seconds');
    decAx.grid(color='gray', linestyle='dotted', linewidth=1)

    decLine.set_data([],[])
    fill_lines_cpu=decAx.fill_between(decLine.get_xdata(),50,0)

    return [decLine] + [fill_lines_cpu]


def updateDecGraph(frame):
    global fill_lines_cpu
    global cpuy_list
    global cpux_list
    global decLine
    global decAx
    global cpu_user_prev
    global cpu_idle_prev
 
    dump=subprocess.check_output(["adb shell cat /sys/bus/platform/drivers/nvdec/54480000.nvdec/load"],shell=True).decode("utf-8")

    #dump=subprocess.check_output(["adb shell cat /sys/kernel/debug/nvdec/actmon_avg"],shell=True).decode("utf-8")
    if dump != "":
        actmon_avg=int(dump.strip())

        cpuy_list.popleft()
    
        cpuy_list.append(actmon_avg/10)

        decLine.set_data(cpux_list,cpuy_list)

        fill_lines_cpu.remove()
        fill_lines_cpu=decAx.fill_between(cpux_list,0,cpuy_list, facecolor='red', alpha=0.50)

    return [decLine] + [fill_lines_cpu]



decAnimation = FuncAnimation(figDec, updateDecGraph, frames=200,
                    init_func=initDecGraph,  interval=50, blit=True)


plt.show()


