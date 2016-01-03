import os, helper, sqlite3, SQLHelper, helper, htmlGen
from config import *

def printCurrentFile(filePath):
    print '<h1>'+helper.getDBNameFromPath(filePath)+'</h1>'

# generare string with approximate time to complete operation
def generateFilesAproximateTimeString(files, caseName):
    s = ""
    for file in files:
        time = helper.getRenderGraphTime(os.path.getsize(CASES_DIR + caseName + PCAP_DIR + file))
        s += file + ":" + str(time) + ";"
    return s


def printInputFilterForm(filePath, caseName):
    info = helper.getReadableFileInfo(helper.getDBNameFromPath(filePath), caseName)
    approximateTime = helper.getRenderGraphTime(os.path.getsize(filePath))
    title = 'Approximate time to render graph is: ' + helper.getReadableTimeInfo(approximateTime)
    originFiles = SQLHelper.loadFiles(caseName, 'origin')
    filteredFiles = SQLHelper.loadFiles(caseName, 'filtered')
    tmpFiles = SQLHelper.loadFiles(caseName, 'tmp')
    filesApproxStr = generateFilesAproximateTimeString(originFiles, caseName)
    filesApproxStr += generateFilesAproximateTimeString(filteredFiles, caseName)
    filesApproxStr += generateFilesAproximateTimeString(tmpFiles, caseName)
    options = '<optgroup label="Original files">'
    for file in originFiles:
        options += '  <option value="'+file+'">'+file+'</option>'
    options += '</optgroup>'
    options += '<option data-divider="true"></option>'
    options += '<optgroup label="Filtered files">'
    for file in filteredFiles:
        options += '  <option value="'+file+'">'+file+'</option>'
    options += '</optgroup>'
    options += '<option data-divider="true"></option>'
    options += '<optgroup label="Temporary files">'
    for file in tmpFiles:
        options += '  <option value="'+file+'">'+file+'</option>'
    allFiles = originFiles + filteredFiles + tmpFiles
    table = '<div id="files" class="collapse">'
    table += '<table id="" class="display" cellspacing="0" width="100%">'
    table += '<thead><tr><th>ID</th><th>Name</th><th>Size</th><th>First Packet</th><th>Last Packet</th><th>Filter</th><th>Source File</th><th>Description</th></tr><tbody>'
    for file in allFiles:
        info = helper.getReadableFileInfo(file, caseName)
        sourceID = str(SQLHelper.getFileID(info[4],caseName)) + '.' if str(SQLHelper.getFileID(info[4],caseName)) != 'None' else ''
        table += '<tr><th>%s</th><th><div class="checkbox"><label><input type="checkbox" value="%s" name="additionalFiles" id="additionalFiles"><b>%s</b></label></div> </th><th>%s</th><th>%s</th><th>%s</th><th>%s</th><th>%s</th><th>%s</th></tr>' % (str(info[6]), file, file, info[1], info[2], info[3], info[0], sourceID + info[4], info[5])
    table += '</tbody></table></div>'
    info = helper.getReadableFileInfo(helper.getDBNameFromPath(filePath), caseName)
    options += '</optgroup>'
    print '<h2>File Details</h2>'
    formStr = '<form action="main.py" class="form-horizontal" method="post">'
    formStr += '<div class="form-group"><label class="col-md-2">Current filter on File:</label>'
    formStr += '<p class="col-md-10 form-control-static">'+info[0]+'</p></div>'
    formStr += '<div class="form-group"><label class="col-md-2">Size:</label>'
    formStr += '<p class="col-md-10 form-control-static">'+info[1]+'</p></div>'
    formStr += '<div class="form-group"><label class="col-md-2">First Packet:</label>'
    formStr += '<p class="col-md-10 form-control-static">'+info[2]+'</p></div>'
    formStr += '<div class="form-group"><label class="col-md-2">Last Packet:</label>'
    formStr += '<p class="col-md-10 form-control-static">'+info[3]+'</p></div>'
    formStr += '<div class="form-group"><label class="col-md-2">Source File:</label>'
    formStr += '<p class="col-md-10 form-control-static">'+info[4]+'</p></div>'
    formStr += '<div class="form-group"><label class="col-md-2">Description:</label>'
    formStr += '<div class="col-md-4"><input type="text" class="form-control" name="description"value="%s" /></div>' % info[5]
    formStr += '<input type="hidden" name="pagesToRender" value="showFile">'
    formStr += '<input type="hidden" name="caseName" value="'+caseName+'"/>'
    formStr += '<input type="hidden" name="filePath" value="'+filePath+'"/>'
    formStr += '<input type="hidden" name="actions" value="editDescription"/>'
    formStr += '<input type="submit" class="btn btn-default" value="Edit" name="Edit"/></div></form>'

    formStr += '<h2>Graph settings</h2>'
    formStr += '<form action="main.py" class="form-horizontal" method="post">'
    formStr += '<div class="form-group"><label class="col-md-2">Time window:</label>'
    formStr += '<div class="col-md-2"><label>From:</label><input type="text" title="Enter date and time in format: YYYY-MM-DD HH:MM:SS" class="form-control" value="%s"name="start"/></div>' % (info[2])
    formStr += '<div class="col-md-2"><label>To:</label><input type="text" title="Enter date and time in format: YYYY-MM-DD HH:MM:SS" class="form-control" value="%s"name="end"/></div><div class="col-md-4">*This condition applies on ALL selected files.</div></div>' % (info[3])
    formStr += '<div class="form-group"><label class="col-md-2">Files to compare:</label>'
    formStr += '<div class="col-md-10"><a data-toggle="collapse" href="#files">Show/Hide</a></div></div>'
    formStr += '<div class="form-group"><div class="col-md-12"> '+table+'</div></div>'
    formStr += '<div class="form-group"><label class="col-md-2">Edit filter:</label>'
    formStr += '<div class="col-md-4"><textarea class="form-control" name="filterContent"></textarea></div><div class="col-md-4">*This condition applies ONLY on primary selected file.</div></div>'
    formStr += '<div class="form-group"><label class="col-md-2">Graph time sample rate(s):</label>'
    formStr += '<div class="col-md-4"><input type="text" title="Enter amount of seconds is one time tick in graph. To low value can cause text label colisions. If empty, default value will be used." class="form-control" name="xtics"/></div></div>'
    formStr += '<div class="form-group"><div class="col-md-6">'
    formStr += '<input type="submit" class="btn btn-default pull-right" title="'+title+'"value="Render Graph" name="renderGraph" id="renderGraph" onclick="var t = getSumTime(\''+filesApproxStr+'\','+str(approximateTime)+');startProgresBar(t);">'
    formStr += '<input type="submit" class="btn btn-default pull-right" title="'+title+'"name="renderDetailedGraph" value="Render Detailed Graph" name="renderDetailedGraph" id="renderDetailedGraph" onclick="var t = getSumTime(\''+filesApproxStr+'\','+str(approximateTime)+');startProgresBar(t);"></div></div>'

    formStr += '<input type="hidden" name="actions" value="applyFilter">'
    formStr += '<input type="hidden" name="pagesToRender" value="showFile:showGraph">'

    formStr += '<input type="hidden" name="caseName" value="'+caseName+'">'
    formStr += '<input type="hidden" name="filePath" value="'+filePath+'">'
    formStr += '</form>'
    print formStr
    print '<hr/>'

    print htmlGen.generateProgresBar()

def printFilter(caseName):
    print 'Current filter on Case: ' + helper.getFilter(caseName)

def render(filePath, caseName, filterContent = None):
    printCurrentFile(filePath)
    printInputFilterForm(filePath, caseName)
