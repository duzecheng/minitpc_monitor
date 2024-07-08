import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

from json import loads, dumps
import pandas as pd
import numpy as np
from time import sleep

with open("sender.txt","r") as file:
    sender = loads(file.readline())

with open("receiver.txt","r") as file:
    receivers = [loads(x) for x in file.read().splitlines()]

def send_email(m):
    server=smtplib.SMTP_SSL(sender['server'], sender['port'])
    server.login(sender['email'], sender['password'])
    for receiver in receivers:
        message = MIMEMultipart()
        message["From"] = formataddr([sender['name'],sender['email']])
        message["To"] = formataddr([receiver['name'],receiver['email']]) 
        message["Subject"] = "Alert"
        
        message.attach(MIMEText(m, "plain"))
        server.sendmail(sender['email'], receiver['email'], message.as_string())
    server.quit()

with open('../python/config.json',"r") as config_file:
    SLEEP = loads(config_file.readline())['sleep']

with open('threshold.json',"r") as thres_file:
    threshold = loads(thres_file.readline())

PATH = "../data/record.log"
TIME_INTERVAL = 500
NUM = int(TIME_INTERVAL / SLEEP)

with open('stop.txt',"r") as flag_file:
    flag =loads(flag_file.readline())

while flag:
    # refresh flag
    with open('stop.txt',"r") as flag_file:
        flag = loads(flag_file.readline())

    with open('hold.txt',"r") as hold_file:
        hold = loads(hold_file.readline())

    data = pd.read_csv(PATH)[-NUM:]
    time = np.array(data['datetime'])[len(data) // 2]

    # print(data['low_pressure'].mean())

    if data['low_pressure'].mean() < threshold['low_pressure'] and (not hold):
        message = f"alert: LP is lower than {threshold['low_pressure']} at {time}."
        send_email(message)
        with open('hold.txt',"w") as hold_file:
            hold_file.write(dumps(1))
        

    sleep(SLEEP)

with open('stop.txt',"w") as flag_file:
    flag_file.write(dumps(1))
with open('hold.txt',"w") as hold_file:
    hold_file.write(dumps(1))