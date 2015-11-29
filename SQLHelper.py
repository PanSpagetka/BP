import sqlite3
from config import *

def getCaseID(caseName):
    conn = sqlite3.connect(DATABASE)
    q = conn.execute("SELECT ID FROM CASES WHERE CASES.NAME = ?", (caseName,))
    ID = q.fetchone()
    conn.close()
    if ID:
        return ID[0]
    return None
def getFileID(fileName, caseName):
    caseID = getCaseID(caseName)
    conn = sqlite3.connect(DATABASE)
    conn.execute('pragma foreign_keys=ON')
    q = conn.execute("SELECT ID FROM FILES WHERE FILES.CASEID = ? AND FILES.FILENAME = ?", (caseID, fileName,))
    #q = conn.execute("SELECT ID FROM FILES WHERE FILES.CASEID = "+str(caseID)+" AND FILES.FILENAME = \'"+fileName+"\'")
    fileID = q.fetchone()
    if fileID is None:
        conn.close()
        return None
    fileID = fileID[0]
    conn.close()
    return fileID

def getCaseAndFilterIDs(caseName):
    conn = sqlite3.connect(DATABASE)
    conn.execute('pragma foreign_keys=ON')
    q = conn.execute("SELECT ID,FILTERID FROM CASES WHERE CASES.NAME = ?",(caseName,))
    IDs = q.fetchone()
    conn.close()
    return IDs
def loadAllFiles(caseName = '*'):
    conn = sqlite3.connect(DATABASE)
    if caseName == '*':
        q = conn.execute("SELECT * FROM FILES")
    else:
        q = conn.execute("SELECT ID FROM CASES WHERE CASES.NAME = ?",(caseName,))
        caseID = q.fetchone()[0]
        q = conn.execute("SELECT FILENAME FROM FILES WHERE CASEID = ?", (caseID,))
    files = []
    for row in q:
        files.append(row[0])
    conn.close()
    return files

def updateFileInfo(fileID, filterID = None, size = None, dateTimes = None):

    conn = sqlite3.connect(DATABASE)
    #conn.execute('pragma foreign_keys=ON')
    '''dbStr = ""
    dbStr += "FILTERID = " + str(filterID) + ", " if filterID else ""
    dbStr += "SIZE = " + str(size)  + ", "if size else ""
    dbStr += "FIRST_PACKET_DATETIME = \'" + str(dateTimes[0]) + "\', LAST_PACKET_DATETIME = \'"+ str(dateTimes[1]) + "\', " if dateTimes else ""
    dbStr = dbStr[:-2]'''
    q = conn.execute("UPDATE FILES SET FILTERID = ?, SIZE = ?, FIRST_PACKET_DATETIME = ?, LAST_PACKET_DATETIME = ? WHERE FILES.ID = ?", (filterID, size, dateTimes[0], dateTimes[1], fileID,))
    conn.commit()
    conn.close()

def getFileInfo(fileID):
    conn = sqlite3.connect(DATABASE)
    q = conn.execute("SELECT FILTERID, SIZE, FIRST_PACKET_DATETIME, LAST_PACKET_DATETIME, SOURCE_FILE FROM FILES WHERE ID = ?",(fileID,))
    info = q.fetchone()
    conn.commit()
    conn.close()
    return info

def loadFiles(caseName = '*', type = "*",  additionalColumn = ''):
    conn = sqlite3.connect(DATABASE)
    if caseName == '*':
        if type == "*":
            q = conn.execute("SELECT * FROM FILES")
        else:
            q = conn.execute("SELECT * FROM FILES WHERE TYPE = ?",(type,))
    else:
        q = conn.execute("SELECT ID FROM CASES WHERE CASES.NAME = ?", (caseName,))
        caseID = q.fetchone()[0]
        if type == "*":
            q = conn.execute("SELECT FILENAME "+additionalColumn+" FROM FILES WHERE CASEID = ?",(str(caseID),))
        else:
            q = conn.execute("SELECT FILENAME "+additionalColumn+" FROM FILES WHERE CASEID = ? AND TYPE = ?",(caseID, type,))
    files = []
    for row in q:
        if additionalColumn == '':
            files.append(row[0])
        else:
            files.append((row[0],row[1]))
    conn.close()
    return files
