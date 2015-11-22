from math import log
from CONSTANTS import *
import os, sqlite3, SQLHelper, subprocess, syslog, datetime
from os.path import isfile, join
unit_list = zip(['bytes', 'kB', 'MB', 'GB', 'TB', 'PB'], [0, 0, 1, 2, 2, 2])

def readableSizeOfFile(filePath):
    num = os.path.getsize(filePath)
    return sizeof_fmt(num)

def getRenderGraphTime(fileSize):
    bytesInMB = 1048576
    fileSize /= bytesInMB
    return (fileSize * BOGOMIPS_TO_RENDER_1MB_GRAPH) / CPU_BOGOMIPS

def getFilterFileTime(fileSize):
    bytesInMB = 1048576
    fileSize /= bytesInMB
    return (fileSize * TIMING_CONSTANT) / HDD_READ_SPEED

def getReadableTimeInfo(seconds):
    if seconds < 10:
        return "few seconds."
    else:
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        if h == 0:
            return "%d m : %d s." % (m, s) if m < 5 else "%d m." % (m)
        else:
            return "%d h :%d m." % (h, m)

def sizeof_fmt(num):
    """Human friendly file size"""
    if num > 1:
        exponent = min(int(log(num, 1024)), len(unit_list) - 1)
        quotient = float(num) / 1024**exponent
        unit, num_decimals = unit_list[exponent]
        format_string = '{:.%sf} {}' % (num_decimals)
        return format_string.format(quotient, unit)
    if num == 0:
        return '0 bytes'
    if num == 1:
        return '1 byte'

def removeFilesFromFolder(folder):
    files = [ f for f in os.listdir(folder) if isfile(join(folder,f)) ]
    for file in files:
        os.remove(folder + file)

# type = case/file
def getFilter(caseName, fileName = None, type = "case"):
    conn = sqlite3.connect(DATABASE)
    if fileName is None:
        q = conn.execute("SELECT FILTERID FROM CASES WHERE CASES.NAME = \'"+caseName+"\'")
        IDs = q.fetchone()
        filterID  = IDs[0]

        q = conn.execute("SELECT CONTENT FROM FILTERS WHERE FILTERS.ID = \'"+str(filterID)+"\'")

        filterContent = q.fetchone()
        # if filter exist set it to its string value else set it to None
        filterContent = filterContent[0] if filterContent else "None"
    else:
        fileID = SQLHelper.getFileID(fileName, caseName)
        q = conn.execute("SELECT FILTERID FROM FILES WHERE FILES.ID = \'"+str(fileID)+"\'")
        IDs = q.fetchone()
        if IDs is None:
            return "None"
        filterID  = IDs[0]

        q = conn.execute("SELECT CONTENT FROM FILTERS WHERE FILTERS.ID = \'"+str(filterID)+"\'")

        filterContent = q.fetchone()
        # if filter exist set it to its string value else set it to None
        filterContent = filterContent[0] if filterContent else filterID

    conn.close()
    return filterContent if filterContent else "None"
def getDirectorySize(dir):
    return sum(os.path.getsize(dir+f) for f in os.listdir(dir) if os.path.isfile(dir+f))

def readableSizeOfDirectory(dir):
    return sizeof_fmt(getDirectorySize(dir))

def clearTmp(caseName):
    removeFilesFromFolder(CASES_DIR + caseName + TMP_DIR + "tmp/")
    removeFilesFromFolder(CASES_DIR + caseName + TMP_DIR)
    removeFilesFromFolder(CASES_DIR + caseName + ORIGIN_DIR + 'tmp/')
    removeFilesFromFolder(CASES_DIR + caseName + ORIGIN_DIR + 'tmp/' + '/tmp')

    conn = sqlite3.connect(DATABASE)
    conn.execute('pragma foreign_keys=ON')
    q = conn.execute("SELECT ID FROM CASES WHERE CASES.NAME = \'"+caseName+"\'")
    caseID = q.fetchone()[0]
    q = conn.execute("DELETE FROM FILES WHERE TYPE = 'tmp' AND CASEID = "+str(caseID))
    conn.commit()
    conn.close()

def getStartDateTimeFromFile(filePath):
    r = subprocess.check_output(['capinfos','-a',filePath])
    r = r.split('\n')
    r = r[1].split('time:')
    return r[1].lstrip()

def getEndDateTimeFromFile(filePath):
    r = subprocess.check_output(['capinfos','-e',filePath])
    r = r.split('\n')
    r = r[1].split('time:')
    return r[1].lstrip()

# return tuple of (first packet datetime, last packet datetime)
def getDateTimeFromFile(filePath):
    syslog.syslog("PCAP APP: getDateTimeFromFile: "+filePath+" started: "+str(datetime.datetime.now()))
    try:
        r = (getStartDateTimeFromFile(filePath), getEndDateTimeFromFile(filePath))
    except subprocess.CalledProcessError:
        syslog.syslog("PCAP APP: getDateTimeFromFile: "+filePath+"   ended: "+str(datetime.datetime.now()))
        return ('DATE PROCESS ERROR', 'DATE PROCESS ERROR')
    syslog.syslog("PCAP APP: getDateTimeFromFile: "+filePath+"   ended: "+str(datetime.datetime.now()))
    return r
def getReadableFileInfo(fileName, caseName):
    fileID = SQLHelper.getFileID(fileName, caseName)
    info = SQLHelper.getFileInfo(fileID)
    if info[0] is None:
        return ["None",sizeof_fmt(info[1]), info[2], info[3], info[4]]

    conn = sqlite3.connect(DATABASE)
    conn.execute('pragma foreign_keys=ON')
    q = conn.execute("SELECT CONTENT FROM FILTERS WHERE ID = "+str(info[0]))
    filterContent = q.fetchone()[0]
    conn.commit()
    conn.close()
    return [filterContent, sizeof_fmt(info[1]), info[2], info[3], info[4]]


def getDBNameFromPath(filePath):
    splitPath = filePath.split('/')
    return splitPath[-2]+'/'+splitPath[-1] if splitPath[-2] != "PCAPs" else splitPath[-1]


def updateFile(filePath, caseName, filterID):
    syslog.syslog("PCAP APP: updateFile: "+filePath+" started: "+str(datetime.datetime.now()))
    fileName = getDBNameFromPath(filePath)
    dateTimes = getDateTimeFromFile(filePath)
    fileSize = os.path.getsize(filePath)
    fileID = SQLHelper.getFileID(fileName, caseName)
    if fileID:
        SQLHelper.updateFileInfo(fileID, filterID, fileSize, dateTimes)
    else:
        conn = sqlite3.connect(DATABASE)
        q = conn.execute("SELECT ID FROM CASES WHERE CASES.NAME = \'"+caseName+"\'")
        caseID = q.fetchone()[0]
        q = conn.execute("INSERT INTO FILES VALUES (null,\'"+fileName+"\',\'filtered\',"+str(caseID)+","+str(filterID)+","+str(fileSize)+",\'"+dateTimes[0]+"\',\'"+ dateTimes[1]+"\')")
        conn.commit()
        conn.close()
    syslog.syslog("PCAP APP: updateFile: "+filePath+"   ended: "+str(datetime.datetime.now()))
