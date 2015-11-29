import os, sqlite3, subprocess, datetime, syslog
from config import *
from Filter import *
from htmlGen import *


def printUploadFileForm(caseName):
    #upload file form
    print '<h2>Upload file</h2>'
    print '<div class="col-md-12">'
    formStr = '<form class="form-horizontal" enctype="multipart/form-data" action="main.py" method="post">'
    formStr += '<input type="hidden" name="actions" value="uploadFile">'
    formStr += '<input type="hidden" name="pagesToRender" value="case:saveFile">'
    formStr += '<input type="hidden" name="caseName" value="'+caseName+'">'
    formStr += '<div class="form-group"><label class="control-label">Select File</label></div>'
    formStr += '<div class="form-group">'
    formStr += '<p>File: <input type="file" name="uploadFileItem"></p>'
    formStr += '<p><input type="submit" class="btn btn-default" value="Upload"></p></div></form>'
    print formStr
    print '</div>'

def checkIfFileIsPCAP(filePath):
    ext = filePath.split('.')
    if len(ext) > 1 and ext[-1] == 'pcap':
        return True
    return False

def removeFile(caseName, filePath):
    fileID = SQLHelper.getFileID(helper.getDBNameFromPath(filePath), caseName)
    conn = sqlite3.connect(DATABASE)
    conn.execute('pragma foreign_keys=ON')
    q = conn.execute("SELECT FILTERID FROM FILES WHERE ID = ?",(fileID,))
    filterID = q.fetchone()[0]
    #remove unused filter
    if filterID is not None:
        q = conn.execute("SELECT ID FROM FILTERS WHERE ID = ?",(filterID,))
        q2 = conn.execute("SELECT ID FROM CASES WHERE FILTERID = ?",(filterID,))
        if len(q.fetchall()) < 2 and len(q2.fetchall()) < 1:
            conn.execute("DELETE FROM FILTERS WHERE ID = ?",(filterID,))
    conn.execute("DELETE FROM FILES WHERE ID = ?",(fileID,))
    conn.commit()
    conn.close()

def addFile(caseName, filePath):
    syslog.syslog("PCAP APP: addFile: "+filePath+" started: "+str(datetime.datetime.now()))
    if not checkIfFileIsPCAP(filePath):
        syslog.syslog("PCAP APP: addFile: "+filePath+"   ended: "+str(datetime.datetime.now()))
        return ("<strong>Error!</strong>File wasnt succesfuly saved. You can upload only PCAP files with .pcap extension.","danger")
    stripFile(filePath)
    fileName = os.path.basename(filePath)
    conn = sqlite3.connect(DATABASE)
    conn.execute('pragma foreign_keys=ON')

    q = conn.execute("SELECT ID,FILTERID FROM CASES WHERE CASES.NAME = ?",(caseName,))
    IDs = q.fetchone()
    caseID = IDs[0]
    filterID  = IDs[1]
    q = conn.execute("SELECT CONTENT FROM FILTERS WHERE FILTERS.ID = ?", (filterID,))
    filterContent = q.fetchone()
    # apply filter and save filtered file
    if filterContent and filterContent != '':
        filteredFileName = applyFilterOnFile(filePath, filterContent[0], caseName)
        filteredFileName = filteredFileName
        # file exists
        if SQLHelper.getFileID(filteredFileName, caseName) is not None:
            conn.close()
            helper.updateFile(CASES_DIR + caseName + PCAP_DIR + filteredFileName, caseName, filterID)
        else:
            sourceFile = helper.getDBNameFromPath(filePath)
            if os.path.isfile(CASES_DIR + caseName + PCAP_DIR + filteredFileName):
                dateTimes = helper.getDateTimeFromFile(CASES_DIR + caseName + PCAP_DIR + filteredFileName)
                fileSize = os.path.getsize(CASES_DIR + caseName + PCAP_DIR + filteredFileName)
                q = conn.execute("INSERT INTO FILES VALUES (null, ?, \'filtered\', ?, ?, ?, ?, ?, ?)", (filteredFileName, caseID, filterID, fileSize, dateTimes[0], dateTimes[1], sourceFile,))
                #q = conn.execute("INSERT INTO FILES VALUES (null,\'"+filteredFileName+"\',\'filtered\',"+str(caseID)+","+str(filterID)+","+str(fileSize)+",\'"+dateTimes[0]+"\',\'"+ dateTimes[1]+"\',\'"+sourceFile+"\')")
                conn.commit()
            else:
                f = open(CASES_DIR + caseName + PCAP_DIR + filteredFileName, 'w')
                f.write("")
                f.close()
                q = conn.execute("INSERT INTO FILES VALUES (null, ?,\'filtered\', ?, ?, 0, \'n/a\', \'n/a\', ?)",(filteredFileName, caseID, filterID, sourceFile,))
                #q = conn.execute("INSERT INTO FILES VALUES (null,\'"+filteredFileName+"\',\'filtered\',"+str(caseID)+","+str(filterID)+",0,\'n/a\',\'n/a\',\'"+sourceFile+"\')")
                conn.commit()
            conn.close()

    dateTimes = helper.getDateTimeFromFile(filePath)
    fileSize = os.path.getsize(filePath)
    # add to db
    # file exist
    if SQLHelper.getFileID(helper.getDBNameFromPath(filePath), caseName) is not None:
        helper.updateFile(filePath, caseName, "null")
    else:
        conn = sqlite3.connect(DATABASE)
        conn.execute('pragma foreign_keys=ON')
        conn.execute("INSERT INTO FILES VALUES (null, ?, ?, ?, null, ?, ?, ?, ?)", ("origin/"+fileName, 'origin', caseID, fileSize, dateTimes[0], dateTimes[1], 'n/a',))
        #conn.execute("INSERT INTO FILES VALUES (null,\'"+"origin/"+fileName+"\',\'origin\',"+str(caseID)+",null"+","+str(fileSize)+",\'"+dateTimes[0]+"\',\'"+dateTimes[1]+"\',\'n/a\')")
        conn.commit()
        conn.close()
    syslog.syslog("PCAP APP: addFile: "+filePath+"   ended: "+str(datetime.datetime.now()))
    return ("<strong>Success!</strong> File was succesfuly saved.","success")

def saveFile(caseName, fileItem):
    if not fileItem.filename:
        return ("No file selected.", 'danger')
    fileName = os.path.basename(fileItem.filename)
    filePath = CASES_DIR + caseName + ORIGIN_DIR + fileName
    dirPath = CASES_DIR + caseName + PCAP_DIR + ORIGIN_DIR

    #save file
    f = open(filePath, 'wb')
    f.write(fileItem.file.read())
    f.close()


    return addFile(caseName, filePath)

def render(caseName):
    printUploadFileForm(caseName)
    #print saveFile(caseName, fileItem)

'''

#!/usr/bin/python

import cgi, os
import cgitb; cgitb.enable()
from config import *
from Filter import *
from htmlGen import *
form = cgi.FieldStorage()

# Get filename here.
fileItem = form['filename']

#generate begining of html
print "Content-Type: text/html\n\n"
print genBegining('File upload')

# Test if the file was uploaded
if fileItem.filename:
   # strip leading path from file name to avoid
   # directory traversal attacks
   fn = os.path.basename(fileItem.filename)
   if form.has_key('casename'):
     filePath = CASES_DIR + form['casename'].value + PCAP_DIR + fn
     dirPath = CASES_DIR + form['casename'].value + PCAP_DIR

     #save file
     f = open(filePath, 'wb')
     f.write(fileItem.file.read())
     f.close()

     filterfilePath = dirPath + FILTER_FILE_NAME
     #check if filter exist and apply it on uploaded file
     if os.path.isfile(filterfilePath):
       #load filter from file
       filterFile = open(filterfilePath,'r')
       filterContent = filterFile.read()
       filterFile.close()

       #remove whitespaces from end of file
       filterContent = filterContent.rstrip()
       #apply filter on file
       applyFilterOnFile(filePath, filterContent)

     #create filter file
     else:
        filterFile = open(filterfilePath,'w')
        filterFile.write('')
        filterFile.close()


     message = 'The file "' + fn + '" was uploaded successfully'


else:
   message = 'No file was uploaded'


print message
#generate link bask to cases page
print genHref(text = 'Back to: ' + form['casename'].value, link = "showCase.py?case=" +form['casename'].value)
print genEnd()
'''
