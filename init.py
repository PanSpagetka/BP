#!/usr/bin/python

import subprocess

def getBogomips():
    cpuinfo = subprocess.check_output(['cat', '/proc/cpuinfo'])
    cpuinfo = cpuinfo.split('\n')
    for line in cpuinfo:
        if line.startswith('bogomips'):
            return line.split(':')[-1]
    return 1
def getHDDReadSpeed():
    hddinfo = subprocess.check_output(['hdparm', '-t', '/dev/sda'])
    hddinfo = hddinfo.split('=')[-1]
    hddinfo = hddinfo.split('MB/sec')[0]
    return float(hddinfo.strip())

if __name__ == "__main__":
    configFile =  open('CONSTANTS.py','r').readlines()
    bogomips = getBogomips()
    hddReadSpeed = getHDDReadSpeed()
    for i in range(len(configFile)):
        if configFile[i].startswith('CPU_BOGOMIPS'):
            configFile[i] = 'CPU_BOGOMIPS = ' + str(bogomips) + '\n'
        elif configFile[i].startswith('HDD_READ_SPEED'):
            configFile[i] = 'HDD_READ_SPEED = ' + str(hddReadSpeed) + '\n'
    f = open('CONSTANTS.py','w')
    f.writelines(configFile)
