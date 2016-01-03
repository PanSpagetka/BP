import cgi
import cgitb, os, Case, helper, sqlite3, SQLHelper, saveFile, syslog, datetime, htmlGen
from htmlGen import *
from config import *

def loadCase(caseName):
    cases = Case.loadFromDB(DATABASE, mode = 'dic')
    if(caseName in cases):
        case = cases[caseName]
        return case
# return all files, if caseName is set, return files from selected case
def loadAllFiles(caseName = '*'):
    conn = sqlite3.connect(DATABASE)
    if caseName == '*':
        q = conn.execute("SELECT * FROM FILES")
    else:
        q = conn.execute("SELECT ID FROM CASES WHERE CASES.NAME = ?",(caseName,))
        caseID = q.fetchone()[0]
        q = conn.execute("SELECT FILENAME FROM FILES WHERE CASEID = ?",(caseID,))
    files = []
    for row in q:
        files.append(row[0])
    conn.close()
    return files

# check if there are new, changed or deleted original files in selected case
def checkOriginFilesConsistency(caseName):
    syslog.syslog("PCAP APP: checkOriginFilesConsistency started: "+str(datetime.datetime.now()))
    originFiles = SQLHelper.loadFiles(caseName, 'origin')
    #files in directory
    files = [f for f in os.listdir(CASES_DIR + caseName + ORIGIN_DIR) if os.path.isfile(os.path.join(CASES_DIR + caseName + ORIGIN_DIR,f))]

    #add orrigin/ prefix to each file
    files = map(lambda fileName: 'origin/'+ fileName, files)

    # check if are some new or deleted files
    newFiles = [file for file in files if file not in originFiles]
    deletedFiles = [file for file in originFiles if file not in files]
    for file in deletedFiles:
        saveFile.removeFile(caseName, CASES_DIR + caseName + PCAP_DIR + file)
    for file in newFiles:
        a = saveFile.addFile(caseName, CASES_DIR + caseName + PCAP_DIR + file)

    # check if files was overwritten
    originFiles = SQLHelper.loadFiles(caseName, 'origin', additionalColumn = ',SIZE')
    for file in originFiles:
        fileSize = os.path.getsize(CASES_DIR + caseName + PCAP_DIR + file[0])
        if file[1] != fileSize:
            saveFile.removeFile(caseName, CASES_DIR + caseName + PCAP_DIR + file[0])
            saveFile.addFile(caseName, CASES_DIR + caseName + PCAP_DIR + file[0])


    syslog.syslog("PCAP APP: checkOriginFilesConsistency   ended: "+str(datetime.datetime.now()))

# check if there are deleted filtered files in selected case
def checkFilteredFileConsistency(caseName):
    syslog.syslog("PCAP APP: checkFilteredFileConsistency started: "+str(datetime.datetime.now()))
    filteredFiles = SQLHelper.loadFiles(caseName, 'filtered')
    #files in directory
    files = [f for f in os.listdir(CASES_DIR + caseName + PCAP_DIR) if os.path.isfile(os.path.join(CASES_DIR + caseName + PCAP_DIR, f))]

    deletedFiles = [file for file in filteredFiles if file not in files]
    for file in deletedFiles:
        saveFile.removeFile(caseName, CASES_DIR + caseName + PCAP_DIR + file)
    syslog.syslog("PCAP APP: checkFilteredFileConsistency   ended: "+str(datetime.datetime.now()))

# print tables with all PCAP files in case
def printPCAPs(case):
    #print all pcap files in this case PCAPs directory
    path = CASES_DIR + case.caseName + PCAP_DIR
    listDir = os.listdir(path)
    originFiles = SQLHelper.loadFiles(case.caseName, 'origin')
    filteredFiles = SQLHelper.loadFiles(case.caseName, 'filtered')
    tmpFiles = SQLHelper.loadFiles(case.caseName, 'tmp')
    print '<h2>Available PCAP files</h2>'
    formStr = '<form action="main.py" class="form-horizontal" method="post">'
    formStr += '<a data-toggle="collapse" href="#originFiles"><h3>Original files: ('+helper.readableSizeOfDirectory(CASES_DIR+case.caseName+ORIGIN_DIR)+')</h3></a>' if originFiles else ""
    formStr += '<div id="originFiles" class="collapse">'
    formStr += '<table id="" class="display" cellspacing="0" width="100%">'
    formStr += '<thead><tr><th>ID</th><th>Name</th><th>Size</th><th>First Packet</th><th>Last Packet</th><th>Filter</th><th>Source File</th><th>Description</th></tr><tbody>'
    originFiles.sort()
    for file in originFiles:
        info = helper.getReadableFileInfo(file,case.caseName)
        formStr += '<tr><th>%s</th><th><div class="radio"><label><input type="radio" value="%s" name="filePath"> <b>%s</b></label></div> </th><th>%s</th><th>%s</th><th>%s</th><th>%s</th><th>%s</th><th>%s</th></tr>' % (str(info[6]),path + file, file, info[1], info[2], info[3], info[0], info[4], info[5])
    formStr += '</tbody></table></div>'
    formStr += '<a data-toggle="collapse" href="#filteredFiles"><h3>Filtered files: ('+helper.readableSizeOfDirectory(CASES_DIR+case.caseName+PCAP_DIR)+')</h3></a>' if filteredFiles else ""
    formStr += '<div id="filteredFiles" class="collapse">'
    formStr += '<table id="" class="display" cellspacing="0" width="100%">'
    formStr += '<thead><tr><th>ID</th><th>Name</th><th>Size</th><th>First Packet</th><th>Last Packet</th><th>Filter</th><th>Source File</th><th>Description</th></tr><tbody>'
    filteredFiles.sort()
    for file in filteredFiles:
        info = helper.getReadableFileInfo(file,case.caseName)
        sourceID = str(SQLHelper.getFileID(info[4],case.caseName)) + '.' if str(SQLHelper.getFileID(info[4],case.caseName)) != 'None' else ''
        formStr += '<tr><th>%s</th><th><div class="radio"><label><input type="radio" value="%s" name="filePath"> <b>%s</b></label></div> </th><th>%s</th><th>%s</th><th>%s</th><th>%s</th><th>%s</th><th>%s</th></tr>' % (str(info[6]),path + file, file, info[1], info[2], info[3], info[0], sourceID + info[4], info[5])
    formStr += '</tbody></table></div>'
    tmpFiles.sort
    if tmpFiles:
        sourceID = str(SQLHelper.getFileID(info[4],case.caseName)) + '.' if str(SQLHelper.getFileID(info[4],case.caseName)) != 'None' else ''
        formStr += '<a data-toggle="collapse" href="#tmpFiles"><h3>Temporary files: ('+helper.readableSizeOfDirectory(CASES_DIR+case.caseName+TMP_DIR)+')</h3></a>'
        formStr += '<div id="tmpFiles" class="collapse">'
        formStr += '<table id="" class="display" cellspacing="0" width="100%">'
        formStr += '<thead><tr><th>ID</th><th>Name</th><th>Size</th><th>First Packet</th><th>Last Packet</th><th>Filter</th><th>Source File</th><th>Description</th></tr><tbody>'
        for file in tmpFiles:
            info = helper.getReadableFileInfo(file,case.caseName)
            formStr += '<tr><th>%s</th><th><div class="radio"><label><input type="radio" value="%s" name="filePath"> <b>%s</b></label></div> </th><th>%s</th><th>%s</th><th>%s</th><th>%s</th><th>%s</th><th>%s</th></tr>' % (str(info[6]),path + file, file, info[1], info[2], info[3], info[0], sourceID + info[4], info[5])
        formStr += '</tbody></table></div>'
    formStr += '<div class="form-group"><div class="col-md-6">'
    formStr += '<input type="submit" class="btn btn-default pull-right" value="Select File" name="selectFile"/>'
    formStr += '<input type="submit" class="btn btn-default pull-left" name="clearTmp" value="Delete All Temporary Files"></div>'
    formStr += '</div>'

    formStr += '<input type="hidden" name="actions" value="deleteFile">'
    formStr += '<input type="hidden" name="pagesToRender" value="showFile"><input type="hidden" name="caseName" value="'+case.caseName+'">'
    formStr += '</form>'
    print formStr
    print '<hr/>'

# print case descriptin
def printCase(case):
    print '<label class="col-md-2">Name:</label>'
    print '<div class="col-md-10"<p>'+case.caseName+'</p></div>'
    print '<label class="col-md-2">Description:</label>'
    print '<div class="col-md-10"<p>'+case.description+'</p></div>'



def printClearTmpButton(caseName):
    print '<div class="col-md-12">'
    formStr = '<form class="form-horizontal" action="main.py" method="post"><br>'
    formStr += '<input type="hidden" name="actions" value="clearTmp">'
    formStr += '<input type="hidden" name="pagesToRender" value="case:saveFile">'
    formStr += '<input type="hidden" name="caseName" value="'+caseName+'">'
    formStr += '<div class="form-group"><input type="submit" class="btn btn-default" value="clearTmp"></div></form>'
    print formStr
    print '</div>'

# print filter form in selected case
def printFilterForm(case):
    oSize = helper.getDirectorySize(CASES_DIR+case.caseName+ORIGIN_DIR)
    fSize = helper.getDirectorySize(CASES_DIR+case.caseName+PCAP_DIR)
    eTime = helper.getFilterFileTime(oSize)
    aTime = helper.getFilterFileTime(fSize)
    eTitle = 'Apply filters on files may take up to ' + helper.getReadableTimeInfo(eTime)
    aTitle = 'Apply filters on files may take up to ' + helper.getReadableTimeInfo(aTime)

    filterContent = helper.getFilter(case.caseName)
    timeFilter = helper.getTimeFilter(case.caseName)
    print '<h2>Edit inicial filter</h2>'
    formStr = '<form class="form-horizontal" action="main.py" method="post">'
    formStr += '<div class="form-group"><label class="col-md-2">Description:</label>'
    formStr += '<p class="col-md-10 form-control-static">'+case.description+'</p></div>'
    formStr += '<input type="hidden" name="actions" value="editFilter">'
    formStr += '<input type="hidden" name="pagesToRender" value="case:saveFile">'
    formStr += '<div class="form-group"><label class="col-md-2">Time window:</label>'
    formStr += '<div class="col-md-2"><label>From:</label><input type="text" title="Enter date and time in format: YYYY-MM-DD HH:MM:SS" class="form-control" name="start" value="'+timeFilter[0]+'"/></div>'
    formStr += '<div class="col-md-2"><label>To:</label><input type="text" title="Enter date and time in format: YYYY-MM-DD HH:MM:SS" class="form-control" name="end" value="'+timeFilter[1]+'"/></div></div>'
    formStr += '<div class="form-group">'
    formStr += '<label class="col-md-2">Inicial filter:</label>'
    formStr += '<div class="col-md-4"><textarea class="form-control" name="filterContent">'+filterContent+'</textarea></div></div>'
    formStr += '<input type="hidden" name="caseName" value="'+case.caseName+'">'
    formStr += '<div class="form-group">'
    formStr += '<div class="col-md-6"><input type="submit" value="Apply on Filtered" class="btn btn-default pull-right" title="'+aTitle+'" onclick="startProgresBar('+str(aTime)+')" name="Append">'
    formStr += '<input type="submit" value="Apply" class="btn btn-default pull-right" title="'+eTitle+'" onclick="startProgresBar('+str(eTime)+')" name="Edit"></div></div></form>'
    print formStr
    print '<hr/>'
    print htmlGen.generateProgresBar()

def render(caseName):
    checkOriginFilesConsistency(caseName)
    checkFilteredFileConsistency(caseName)
    case = loadCase(caseName)
    # if case exists
    if case:
        print '<h1>'+caseName+'</h1>'
        print '<hr/>'
        printFilterForm(case)
        printPCAPs(case)
