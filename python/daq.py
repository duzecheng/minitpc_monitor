import time

from lakeshore import Model336

from datetime import datetime

import sqlite3

import socket
from json import loads, dumps
from os import system

with open('config.json',"r") as config_file:
    config = loads(config_file.readline())

ADDRESS = config['address']
PORT = config['port']
LENGTH = config['length']
SLEEP = config['sleep']
LOG_INTERVAL = config['log_interval']
DB_SIZE = config['db_size']
LOG_PATH = config['log']
DB_PATH = config['db']


# read data
def daq(address, port):
    s = socket.socket()
    host = address
    port = port
    s.connect((host, port))
    r = loads(s.recv(1024).decode())
    s.close()
    return r


my_model_336 = Model336(ip_address='169.254.149.38')
# Obtain the output percentage of output 1 and print it to the console
heater_one_output = my_model_336.get_heater_output(1)


# LOG_INTERVAL
log = 0
with open(LOG_PATH,"w") as ini_file1:
    ini_file1.write('datetime,tempA,tempB,massA,massB,high_pressure,low_pressure,vaccum,flow\n')

# DB_SIZE
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("PRAGMA auto_vacuum = FULL;")
cursor = list(c.execute("SELECT ROWID FROM minitpc ORDER BY ROWID DESC LIMIT 1;"))
db = 0 if len(cursor) == 0 else cursor[0][0]
conn.commit()
conn.close()

interval = 0

with open('stop.txt',"r") as flag_file:
    flag =loads(flag_file.readline())

while flag:
    # refresh flag
    with open('stop.txt',"r") as flag_file:
        flag = loads(flag_file.readline())
        
    # obtain data
    try:
        for ch in ['A','B']:
            globals()['temp_' + ch] = my_model_336.get_celsius_reading(ch)
    except Exception as e:
        print(f"Obtaining data from Model336. Exception: {e}")
        continue
    result = daq(ADDRESS, PORT)
    if not isinstance(result, list):
        print(f"Obtaining data from modbus device.")
        continue
    
    mass = [1.253722826087 * (result[i])/4095 * 20 - 4.685362318841063 for i in [1, 0]]
    press = [(0.625 * result[2]) / 4095 * 20 - 2.5, (31.25 * result[3]) / 4095 * 20 - 125]
    press[1] += 1.0683760683760681
    fw = 3.09375 * result[4] / 3276 * 20 - 11.875 - 0.4962225274725274
    vacc = result[5]

    # Get the current time in seconds since the Epoch
    current_time = time.time()
    # Convert it to a datetime object
    readable_time = datetime.fromtimestamp(current_time)
    # Format the datetime object as a string in a human-readable format
    formatted_time = readable_time.strftime("%Y-%m-%d %H:%M:%S")
    
    with open(LOG_PATH,"a") as file1:
        file1.write(dumps([formatted_time, temp_A, temp_B, mass[0], mass[1], press[0], press[1], vacc, fw])[1:-1] + '\n')
    log = log + 1

    if log > LENGTH:
        system(f"sed -i '' '2,{log-LENGTH+1}d' record.log")
        log = LENGTH

    interval = interval + 1

    # record data in database
    if interval > LOG_INTERVAL:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("PRAGMA auto_vacuum = FULL;")
        c.execute("INSERT INTO minitpc (datetime, tempA_C, tempB_C, massA_kg, massB_kg, high_pressure_Mpa, low_pressure_kpa, vaccum_pa, flow_L_min)\
        VALUES (?,?,?,?,?,?,?,?,?)",\
                  (formatted_time, temp_A, temp_B, mass[0], mass[1], press[0], press[1], vacc, fw))

        db = db + 1

        # remove the oldest data if the size of database reaches DB_SIZE
        if db > DB_SIZE:
            c.execute("DELETE FROM minitpc WHERE ROWID <= ?;", (db - DB_SIZE,))
            c.execute("UPDATE minitpc SET ROWID = ROWID - ?;", (db - DB_SIZE,))
            db = DB_SIZE

        conn.commit()
        conn.close()
        
        interval = 0
    
    time.sleep(SLEEP)

with open(LOG_PATH,"w") as stop_file1:
    stop_file1.write('datetime,tempA,tempB,massA,massB,high_pressure,low_pressure,vaccum,flow\n')

with open('stop.txt',"w") as flag_file:
    flag_file.write(dumps(1))