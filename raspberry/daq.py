import serial
import minimalmodbus
from pymodbus.client import ModbusSerialClient as ModbusClient

import pymodbus
from pymodbus.pdu import ModbusRequest
from pymodbus.transaction import ModbusRtuFramer

from math import nan

import json
import socket
from pathlib import Path


# obtain data from modbus devices
def read_rs(port, slave, register_address, number_of_registers, baudrate=9600, bytesize=8, parity=serial.PARITY_NONE, stopbits=1, timeout=0.05, mode=minimalmodbus.MODE_RTU):
    instrument = minimalmodbus.Instrument(port, slave)  # port name, slave address (in decimal)
    instrument.serial.port = port                     # this is the serial port name
    instrument.serial.baudrate = baudrate         # Baud
    instrument.serial.bytesize = bytesize
    instrument.serial.parity   = parity
    instrument.serial.stopbits = stopbits
    instrument.serial.timeout  = timeout        # seconds
    instrument.address = slave                         # this is the slave address number
    instrument.mode = mode   # rtu or ascii mode
    return instrument.read_registers(register_address, number_of_registers)

# convert series to vaccum data
def vacc_convert(series):
    temp = (series[0] // 256 - 0x30) + 0.1 * (series[0] % 256 - 0x30)
    temp = temp * 10 ** (series[1] % 256 - 0x30) if series[1] // 256 == 0x2b else temp * 10 ** (0x30 - series[1] % 256)
    return temp


s = socket.socket()

config = json.loads(Path("config.json").read_text())
s.bind((config['host'], config['port']))
print("socket success!")
s.listen(5)
while True: 
    
    c,addr = s.accept()

    try:
        result = read_rs('/dev/ttyUSB2', 1, 0, 4)
        result.append(read_rs('/dev/ttyUSB0', 1, 0, 1, baudrate=4800)[0])
        result.append(vacc_convert(read_rs('/dev/ttyUSB1', 1, 0x6b, 2)))
        c.send(json.dumps(result).encode())
    except Exception as e:
        c.send(json.dumps(nan).encode())
    
    c.close()
