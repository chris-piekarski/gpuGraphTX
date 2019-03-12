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

figCpu,cpuAx = plt.subplots()
figGpu,gpuAx = plt.subplots()
figMem,memAx = plt.subplots()


figGpu.set_facecolor('#F2F1F0')
figGpu.canvas.set_window_title('GPU Activity Monitor')

figCpu.set_facecolor('#F2F1F0')
figCpu.canvas.set_window_title('CPU Activity Monitor')

figMem.set_facecolor('#F2F1F0')
figMem.canvas.set_window_title('Memory Activity Monitor')


# For the comparison
gpuLine, = gpuAx.plot([],[])
cpuLine, = cpuAx.plot([],[])
memLine, = memAx.plot([],[])
memCachedLine, = memAx.plot([],[])
memCachedLine.set_label('Cached')
memLine.set_label('Used')
memAx.legend()

# The line points in x,y list form
gpuy_list = deque([0]*240)
gpux_list = deque(np.linspace(60,0,num=240))
# The line points in x,y list form
cpuy_list = deque([0]*240)
cpux_list = deque(np.linspace(60,0,num=240))
# The line points in x,y list form
memy_list = deque([0]*240)
memcy_list = deque([0]*240)
memx_list = deque(np.linspace(60,0,num=240))

fill_lines_gpu=0
fill_lines_cpu=0
fill_lines_mem=0
fill_lines_memc=0

cpu_user_prev=0
cpu_idle_prev=0

def initMemGraph():
    global memAx
    global memLine
    global fill_lines_mem

    memAx.set_xlim(60, 0)
    memAx.set_ylim(-5, 105)
    memAx.set_title('Memory History')
    memAx.set_ylabel('Memory Usage (%)')
    memAx.set_xlabel('Seconds');
    memAx.grid(color='gray', linestyle='dotted', linewidth=1)

    memLine.set_data([],[])
    memCachedLine.set_data([],[])
    fill_lines_mem=memAx.fill_between(memLine.get_xdata(),50,0)

    return [memLine] + [fill_lines_mem]


def initGpuGraph():
    global gpuAx
    global gpuLine
    global fill_lines_gpu

    gpuAx.set_xlim(60, 0)
    gpuAx.set_ylim(-5, 105)
    gpuAx.set_title('GPU History')
    gpuAx.set_ylabel('GPU Usage (%)')
    gpuAx.set_xlabel('Seconds');
    gpuAx.grid(color='gray', linestyle='dotted', linewidth=1)

    gpuLine.set_data([],[])
    fill_lines_gpu=gpuAx.fill_between(gpuLine.get_xdata(),50,0)

    return [gpuLine] + [fill_lines_gpu]

def initCpuGraph():
    global cpuAx
    global cpuLine
    global fill_lines_cpu

    cpuAx.set_xlim(60, 0)
    cpuAx.set_ylim(-5, 105)
    cpuAx.set_title('CPU History')
    cpuAx.set_ylabel('CPU Usage (%)')
    cpuAx.set_xlabel('Seconds');
    cpuAx.grid(color='gray', linestyle='dotted', linewidth=1)

    cpuLine.set_data([],[])
    fill_lines_cpu=cpuAx.fill_between(cpuLine.get_xdata(),50,0)

    return [cpuLine] + [fill_lines_cpu]

def updateMemGraph(frame):
    global fill_lines_mem
    global fill_lines_memc
    global memy_list
    global memcy_list
    global memx_list
    global memLine
    global memCachedLine
    global memAx
 
    x=subprocess.check_output(["adb shell cat /proc/meminfo"],shell=True)
    if x != "":
	x=x.split()
    	memTotal=x[1]
    	memAvail=x[7]
    	memCach=x[13]
        memy_list.popleft()
        memcy_list.popleft()
	usedMem=int(memTotal)-int(memAvail)
        perctCached=float(memCach)/float(memTotal)
	perctUsed=float(usedMem/float(memTotal))
	#print(perctCached*100)
        memy_list.append(perctUsed*100)
	memcy_list.append(perctCached*100)

        memLine.set_data(memx_list,memy_list)
        memCachedLine.set_data(memx_list,memcy_list)

        fill_lines_mem.remove()
        fill_lines_mem=memAx.fill_between(memx_list,0,memy_list, facecolor='cyan', alpha=0.50)
        fill_lines_memc=memAx.fill_between(memx_list,0,memcy_list, facecolor='brown', alpha=0.50)


    return [memLine] + [fill_lines_mem] + [memCachedLine] + [fill_lines_memc]

def updateGpuGraph(frame):
    global fill_lines_gpu
    global gpuy_list
    global gpux_list
    global gpuLine
    global gpuAx
 
    x=subprocess.check_output(["adb shell cat /sys/devices/gpu.0/load"],shell=True)
    if x != "":
        gpuy_list.popleft()
        # The GPU load is stored as a percentage * 10, e.g 256 = 25.6%
        gpuy_list.append(int(x)/10)

        gpuLine.set_data(gpux_list,gpuy_list)

        fill_lines_gpu.remove()
        fill_lines_gpu=gpuAx.fill_between(gpux_list,0,gpuy_list, facecolor='yellow', alpha=0.30)

    return [gpuLine] + [fill_lines_gpu]

#Calculate realtime from /proc/stat
def updateCpuGraph(frame):
    global fill_lines_cpu
    global cpuy_list
    global cpux_list
    global cpuLine
    global cpuAx
    global cpu_user_prev
    global cpu_idle_prev
 
    dump=subprocess.check_output(["adb shell cat /proc/stat"],shell=True).decode("utf-8")
    if dump != "":
        dump=dump.split("\n")
        tl=dump[0].split()
        cpu_user=int(tl[1])+int(tl[2])+int(tl[3])+int(tl[4])+int(tl[5])+int(tl[6])+int(tl[7])
        cpu_idle=int(tl[4])

        if cpu_user_prev == 0 or cpu_idle_prev == 0:
            cpu_user_prev = cpu_user
            cpu_idle_prev = cpu_idle
            return [ ]

        diff_user=cpu_user - cpu_user_prev
        diff_idle=cpu_idle - cpu_idle_prev
        diff_usage=(1000*(diff_user-diff_idle)/diff_user+5)/10
        
        cpu_user_prev=cpu_user
        cpu_idle_prev=cpu_idle

        cpuy_list.popleft()
    
        cpuy_list.append(round(float(diff_usage)))

        cpuLine.set_data(cpux_list,cpuy_list)

        fill_lines_cpu.remove()
        fill_lines_cpu=cpuAx.fill_between(cpux_list,0,cpuy_list, facecolor='red', alpha=0.50)

    return [cpuLine] + [fill_lines_cpu]



# Keep a reference to the FuncAnimation, so it does not get garbage collected
gpuAnimation = FuncAnimation(figGpu, updateGpuGraph, frames=200,
                    init_func=initGpuGraph,  interval=250, blit=True)
cpuAnimation = FuncAnimation(figCpu, updateCpuGraph, frames=200,
                    init_func=initCpuGraph,  interval=500, blit=True)
memAnimation = FuncAnimation(figMem, updateMemGraph, frames=200,
                    init_func=initMemGraph,  interval=500, blit=True)




plt.show()


