# ShieldInfoGraphTX
A very simple moving graph of GPU & CPU activity for the NVIDIA Shield Tegra. This allows visualization of GPU & CPU utilization over ADB.

![GPU Activity Window](https://github.com/jetsonhacks/gpuGraphTX/blob/master/gpuGraph.png)
![CPU Activity Window](https://github.com/jetsonhacks/gpuGraphTX/blob/master/cpuGraph.png)


The graph is implemented as an animated Python Matplotlib graph. The app requires the Python Matplotlib library.

For Python 2.7, Matplotlib may be installed as follows:

$ sudo apt-get install python-matplotlib

For Python 3, Matplotlib may be installed as follows:

$ sudo apt-get install python3-matplotlib

You can run the app:

$ ./shieldGraph.py

or:

$ python shieldGraph.py

or:

$ python3 shieldGraph.py

<h2>Release Notes</h2>

Forked from jetsonhacks on 1/15/2019
* Use ADB for use on SHIELD
* Add second graph for CPU usage

Initial Release May, 2018
* L4T 28.2 (JetPack 3.2)
* Tested on Jetson TX2
* Tested on Jetson TX1

