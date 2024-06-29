# Project
This project aims to obtain data from miniTPC, show data as a plot, and save data for future analysis.

Code to obtain and save data is saved as ./python/daq.py, and configurations is saved as config.json in the same directory. The file stop.txt in the same directory is used to control the code. To terminate the code, change 1 to 0 in stop.txt.

Data are saved in ./data/. The csv file record.log is used to make the plot and data.db is used to save data for analysis.

./monotor.py reads data from ./data/record.log and makes a plot to show the status of miniTPC. It is written with package plotly and dash frame. After running the code, it will set up a server and you can access it.

## Paspberry Pi
The Raspberry pi is used to obtain data from modbus device. Some information is shown as follows.

OS: Raspberry Pi OS(64-bit)

Wifi: Xiaomi_CCDF_5G

Host name: minitpc.local

User name: ihep101, password: minitpc

The daq code is saved as ~/temp_dzc/python/daq.py, and configurations is saved as config.json in the same directory. For convenience of management, a copy is saved in ./raspberry in the project. After running the code, a socket server is set up and you can obtain data with daq.py in ./python/daq.py in the project.

Before running the code, please enter command mbus to enter virtual environment mbus. Since python package installation is not allowed in real envirionment, please use a virtual envirionment. conda is not installed, so use venv and pip in python to create virtual envirionment and install packages.

Jupyter-lab is installed in raspberry pi. To use it, please use ssh tunneling to port 8889, namely use command ssh ihep101@minitpc.local -L [local port]:minitpc.local:8889. Then enter the environment mbus, start jupyter-lab, enter localhost:[local port] on your browser to access jupyter-lab, and enter minitpc as the password for jupyter-lab.