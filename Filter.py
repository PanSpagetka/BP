import os, subprocess, sqlite3, SQLHelper, helper, syslog, datetime
from CONSTANTS import *

# takes file to filter and filter
# returns new filtered file
def applyFilterOnFile(filepath, filterContent, caseName = None, tmp = False):
    syslog.syslog("PCAP APP: applyFilterOnFile: "+filepath+" started: "+str(datetime.datetime.now()))
    filepath = os.path.abspath(filepath)
    dirpath = CASES_DIR + caseName + PCAP_DIR if caseName else os.path.dirname(filepath) + '/'
    dirpath += "tmp/" if tmp else ""

    outputFileName = os.path.basename(filepath).split('.')
    outputFileName = outputFileName[0] + 'F' + '.pcap'

    #to e ono
    r = subprocess.call(['PCAPtools/pcap_filter','-f',filterContent, '-o',dirpath+outputFileName, '-i',filepath])

    #os.system('captcp show --match ' + filterContent + filepath + ' > ' + filepath + 'Filtered')
    ######fungovalo subprocess.check_output(['tcpdump', '-r', filepath,'-w', dirpath+outputFileName, filterContent])
    #subprocess.check_output(['tcpdump', '-r', filepath])
    #filteredFile.write(['tcpdump', '-r', filepath,'-w', filepath, 'F', filterContent])
    syslog.syslog("PCAP APP: applyFilterOnFile: "+filepath+"   ended: "+str(datetime.datetime.now()))
    return outputFileName

def stripFile(filePath):
    syslog.syslog("PCAP APP: stripFile: "+filePath+" started: "+str(datetime.datetime.now()))
    dirpath = os.path.dirname(filePath)
    outputFileName = 'tmp.pcap'
    r = subprocess.call(['PCAPtools/pcap_filter','-s', '-o',dirpath+outputFileName, '-i',filePath])
    os.rename(dirpath+outputFileName, filePath)
    syslog.syslog("PCAP APP: stripFile: "+filePath+"   ended: "+str(datetime.datetime.now()))

def applyTimeFilterOnFile(filePath, caseName, start = '', end = ''):
    if start == '' and end == '':
        return None
    outputFileName = os.path.basename(filePath).split('.')[0] + start.replace(' ', '-') + '-' + end.replace(' ', '-') + '.pcap'
    outputFilePath = CASES_DIR + caseName + TMP_DIR + outputFileName
    subprocess.call(['editcap','-A', start, '-B',end, filePath,outputFilePath])
    if not os.path.isfile(outputFilePath):
        return None
    conn = sqlite3.connect(DATABASE)
    conn.execute('pragma foreign_keys=ON')
    # crete new fitler in db
    q = conn.execute("SELECT ID FROM CASES WHERE CASES.NAME = \'"+caseName+"\'")
    IDs = q.fetchone()
    caseID = IDs[0]
    if SQLHelper.getFileID(helper.getDBNameFromPath(outputFilePath), caseName) is not None:
        conn.commit()
        conn.close()
        helper.updateFile(outputFilePath, caseName, 'null')
    else:
        sourceFile = helper.getDBNameFromPath(filePath)
        fileSize = os.path.getsize(outputFilePath)
        dateTimes = helper.getDateTimeFromFile(outputFilePath)
        conn.execute("INSERT INTO FILES VALUES (null,\'"+"tmp/"+outputFileName+"\',\'tmp\',"+str(caseID)+",null,"+str(fileSize)+",\'"+dateTimes[0]+"\',\'"+ dateTimes[1]+"\',\'"+sourceFile+"\')")
        conn.commit()
        conn.close()
    return outputFilePath


def applyTmpFilter(filePath, filterContent, caseName):
    currentFilter = helper.getFilter(caseName, helper.getDBNameFromPath(filePath), type = 'file')
    filteredFileName = applyFilterOnFile(filePath, filterContent, caseName, True)
    if not os.path.isfile(CASES_DIR + caseName + TMP_DIR + filteredFileName):
        return None
    summFilter = currentFilter + ' && ' + filterContent if currentFilter != 'None' else filterContent
    conn = sqlite3.connect(DATABASE)
    conn.execute('pragma foreign_keys=ON')
    # crete new fitler in db
    conn.execute("INSERT INTO FILTERS VALUES(null, \'"+summFilter+"\')")
    q = conn.execute('SELECT max(ID) FROM FILTERS')
    filterID = q.fetchone()[0]
    q = conn.execute("SELECT ID FROM CASES WHERE CASES.NAME = \'"+caseName+"\'")
    IDs = q.fetchone()
    caseID = IDs[0]
    if SQLHelper.getFileID(helper.getDBNameFromPath(CASES_DIR + caseName + TMP_DIR + filteredFileName), caseName) is not None:
        conn.commit()
        conn.close()
        helper.updateFile(CASES_DIR + caseName + TMP_DIR + filteredFileName, caseName, filterID)
    else:
        sourceFile = helper.getDBNameFromPath(filePath)
        fileSize = os.path.getsize(CASES_DIR + caseName + TMP_DIR + filteredFileName)
        dateTimes = helper.getDateTimeFromFile(CASES_DIR + caseName + TMP_DIR + filteredFileName)
        conn.execute("INSERT INTO FILES VALUES (null,\'"+"tmp/"+filteredFileName+"\',\'tmp\',"+str(caseID)+","+str(filterID)+","+str(fileSize)+",\'"+dateTimes[0]+"\',\'"+ dateTimes[1]+"\',\'"+sourceFile+"\')")
        conn.commit()
        conn.close()
    return filteredFileName

# mode = edit/append, default is edit
def applyFilterOnCase(caseName, newFilter, mode = "edit"):
    syslog.syslog("PCAP APP: applyFilterOnCase: "+caseName+" started: "+str(datetime.datetime.now()))
    IDs = SQLHelper.getCaseAndFilterIDs(caseName)
    if IDs is None:
        return
    caseID = IDs[0]
    filterID = IDs[1]
    conn = sqlite3.connect(DATABASE)
    conn.execute('pragma foreign_keys=ON')

    if mode == "edit":
        if filterID:
            q = conn.execute("UPDATE FILTERS SET CONTENT = \'"+newFilter+"\' WHERE FILTERS.ID = "+str(filterID))
        else:
            q = conn.execute("INSERT INTO FILTERS VALUES(null, \'"+newFilter+"\')")
            q = conn.execute('SELECT max(ID) FROM FILTERS')
            filterID = q.fetchone()[0]
            q = conn.execute("UPDATE CASES SET FILTERID = "+str(filterID)+" WHERE CASES.ID = "+str(caseID))
        q = conn.execute("SELECT FILENAME FROM FILES WHERE FILES.TYPE = \'origin\'AND FILES.CASEID = "+str(caseID))
    else:
        q = conn.execute("SELECT CONTENT FROM FILTERS WHERE FILTERS.ID = "+str(filterID))
        currentFilter = q.fetchone()
        currentFilter = currentFilter[0]
        newFilter = currentFilter + " && " + newFilter
        q = conn.execute("UPDATE FILTERS SET CONTENT = \'"+newFilter+"\' WHERE FILTERS.ID = "+str(filterID))
        q = conn.execute("SELECT FILENAME FROM FILES WHERE FILES.TYPE = \'filtered\' AND FILES.CASEID = "+str(caseID))
    files = []
    a = open("DB/NAME.TXT","w")
    for row in q:
        files.append(CASES_DIR + caseName + PCAP_DIR + row[0])
    conn.commit()
    conn.close()
    for file in files:
        filteredFileName = applyFilterOnFile(file, newFilter, caseName)
        if mode == "append":
            os.rename(CASES_DIR + caseName + PCAP_DIR + filteredFileName, file)
            filteredFileName = os.path.basename(file)
        helper.updateFile(CASES_DIR + caseName + PCAP_DIR + filteredFileName, caseName, filterID)
    syslog.syslog("PCAP APP: applyFilterOnCase: "+caseName+"   ended: "+str(datetime.datetime.now()))
