import os, helper, sqlite3, SQLHelper, helper, htmlGen
from config import *

def printCurrentFile(filePath):
    print '<h1>'+helper.getDBNameFromPath(filePath)+'</h1>'
#    print 'Current file: ' + os.path.basename(filePath) + '<br>'
#    print 'File size: ' + helper.readableSizeOfFile(filePath) + '<br>'

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
    table += '<thead><tr><th>Name</th><th>Size</th><th>First Packet</th><th>Last Packet</th><th>Filter</th><th>Source File</th><th>Description</th></tr><tbody>'
    for file in allFiles:
        info = helper.getReadableFileInfo(file, caseName)
        table += '<tr><th><div class="checkbox"><label><input type="checkbox" value="%s" name="additionalFiles" id="additionalFiles"><b>%s</b></label></div> </th><th>%s</th><th>%s</th><th>%s</th><th>%s</th><th>%s</th><th>%s</th></tr>' % (file, file, info[1], info[2], info[3], info[0], info[4], info[5])
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
    #formStr += '<div class="col-md-4"><select multiple class="form-control" size="6" id="additionalFiles" title="Enter filter in tcpdump format" name="additionalFiles">'+options+'</select></div></div>'
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

    #print '<div class="progress"><div class="progress-bar" role="progressbar" aria-valuenow="70"aria-valuemin="0" aria-valuemax="100" style="width:70%"><spanclass="sr-only">70% Complete</span></div></div>'
    print htmlGen.generateProgresBar()
    #print script
    #print '<script>document.getElementById("progress-bar").style.width = "100px";</script>'
    #print '<form method="post">New filter:<br><textarea name="filter"></textarea><br><br><input type="hidden" name="fileName" value="'+filePath+'"><input type="hidden" name="caseName" value="'+caseName+'"><input type="submit" value="Render Graph"></a></form> '

def printFilter(caseName):
    print 'Current filter on Case: ' + helper.getFilter(caseName)

def render(filePath, caseName, filterContent = None):
    printCurrentFile(filePath)
    #printFilter(caseName)
    printInputFilterForm(filePath, caseName)



'''
#!/usr/bin/python

import cgi, cgitb, os
from htmlGen import *
from Case import *
from config import *
from Filter import *

cgitb.enable()

# generate begining of html
print "Content-Type: text/html\n\n"
print genBegining('showPCAPFILEDetails')

form = cgi.FieldStorage()
#if do NOT applying new filter
if form.has_key('fileName') and not form.has_key('filter') and form.has_key('caseName'):
	filePath = form['fileName'].value
	dirpath = os.path.dirname(form['fileName'].value) + '/'
	filterfilePath = dirpath + FILTER_FILE_NAME
	print 'Current file: ' + os.path.basename(filePath) + '<br>'
	#check if filter file exist, open a print its content
	if os.path.isfile(filterfilePath):
		filterFile = open(filterfilePath, 'r')
		filterFileContent = filterFile.read()
		filterFile.close()
		print 'Current filter: ' + filterFileContent
	#create filter file is not existing
	else:
		filterFile = open(filterfilePath, 'w')
	 	filterFile.close()
		print 'Current filter: None'

	print '<br></br>'
	print '<form method="post">New filter:<br><textarea name="filter"></textarea><br><br><input type="hidden" name="fileName" value="'+filePath+'"><input type="hidden" name="caseName" value="'+form['caseName'].value+'"><input type="submit" value="Apply"></a></form> '

	#render graph button
	#print '<form action="renderGraph.py" method="post"><input type="hidden" name="filter" value="None"><input type="hidden" name="fileName" value="'+filePath+'"><input type="hidden" name="caseName" value="'+form['caseName'].value+'"><input type="submit" value="Render graph"></a></form> '



#if applying new filter
if form.has_key('fileName') and form.has_key('filter') and form.has_key('caseName'):
	filePath = form['fileName'].value
	dirpath = os.path.dirname(form['fileName'].value) + '/'
	print 'Current file: ' + os.path.basename(filePath) + '<br>'

	#display static filter
	filterfilePath = dirpath + FILTER_FILE_NAME
	filterFile = open(filterfilePath,'r')
	filterContent = filterFile.read()
	filterFile.close()
	print 'Current static filter: ' + filterContent
	print '<br></br>'

	#display and apply temporary/dynamic filter
	filterContent = form['filter'].value
	print 'Current temporary filter: ' + filterContent
	print '<br></br>'
	print '<form method="post">New filter:<br><textarea name="filter"></textarea><br><br><input type="hidden" name="fileName" value="'+filePath+'"><input type="hidden" name="caseName" value="'+form['caseName'].value+'"><input type="submit" value="Apply"></a></form> '
	filteredfilePath = dirpath + applyFilterOnFile(filePath, filterContent)

	#print '<form action="renderGraph.py" method="post"><input type="hidden" name="filter" value="None"><input type="hidden" name="fileName" value="'+filePath+'"><input type="hidden" name="caseName" value="'+form['caseName'].value+'"><input type="submit" value="Render graph"></a></form> '
	print '<img width="400" src="renderGraph.py?fileName='+filteredfilePath+'">'


	#print '<img width="400" src="renderGraph.py?case='+case.caseName+'&caseName='+form['caseName'].value+'">'

	#print '<form action = "renderGraph.py?fileName='+ filePath +'"><input type="submit" value="Render graph"></a></form> '

	#print '<form action = "renderGraph.py" method="post"><br><br><input type="hidden" name="fileName" value="'+filePath+'"><input type="hidden" name="filter" value="'+filterContent+'"><input type="hidden" name="caseName" value="'+form['caseName'].value+'"><input type="submit" value="Render graph"></a></form> '


#return to root case page
if form.has_key('caseName'):
	print genHref(text = 'Back to: ' + form['caseName'].value, link = "showCase.py?case=" +form['caseName'].value)
# generate end of html
print genEnd()
'''
