#!/usr/bin/python

import cgi
import cgitb, os
import cases, showCase, showPCAPFileDetails, Filter, renderGraph, saveFile, helper, syslog
from htmlGen import *
from config import *
from subprocess import CalledProcessError


cgitb.enable()

form = cgi.FieldStorage()
pagesToRender = "default"
actions = []
message = ""
messageType = "warning"
if form.has_key('pagesToRender'):
    pagesToRender = form['pagesToRender'].value.split(':')
if form.has_key('actions'):
    actions = form['actions'].value.split(':')
caseName = form['caseName'].value if form.has_key('caseName') else ""
fileName = os.path.basename(form['filePath'].value) if form.has_key('filePath') else ""

# ---------------ACTIONS-------------------
# begining of action section, here are executed all actions
if "addCase" in actions:
    if form.has_key('caseName') and form.has_key('caseDescription'):
        ret = cases.addCase(form['caseName'].value, form['caseDescription'].value)
        message = ret[0]
        messageType = ret[1]
    else:
        message = "<strong>Warning!</strong> Please enter Case Name and Case Description."
        messageType = 'warning'
# when editing filter on case, if filter is empty this action will be skipped
if 'editFilter' in actions:
    filterContent = form['filterContent'].value if form.has_key("filterContent") else ''
    start = form['start'].value if form.has_key('start') else ''
    end = form['end'].value if form.has_key('end') else ''
    if form.has_key("Edit"):
        Filter.applyFilterOnCase(form['caseName'].value, filterContent , mode = "edit", start = start, end = end)
    else:
        Filter.applyFilterOnCase(form['caseName'].value, filterContent, mode = "append", start = start, end = end)
    message = "<strong>Success!</strong> Filter was applied"
    messageType = 'success'

# when applying filter on currently selected file, crete new tmp file
if "applyFilter" in actions:
    start = form['start'].value if form.has_key('start') else ''
    end = form['end'].value if form.has_key('end') else ''
    syslog.syslog("PCAP APP:  "+start +'    ' + end)
    if form.has_key('filterContent'):
        filteredFileName = Filter.applyTmpFilter(form['filePath'].value, form['filterContent'].value, form['caseName'].value)
        if filteredFileName:
            form['filePath'].value = CASES_DIR + form['caseName'].value + TMP_DIR + filteredFileName
            fileName = filteredFileName
        else:
            pagesToRender.remove(renderGraph)
            message = "<strong>Error!</strong> Rendering graph Error, make sure you use right filter syntax."
            messageType = "error"
    if start and end:
        ret = Filter.applyTimeFilterOnFile(form['filePath'].value, caseName, start, end, override = False)
        form['filePath'].value = ret


if "uploadFile" in actions:
    if form.has_key('caseName') and form.has_key('uploadFileItem'):
        ret = saveFile.saveFile(form['caseName'].value, form['uploadFileItem'])
        message = ret[0]
        messageType = ret[1]
    else:
        message = "You have to choose a file."

if "deleteFile" in actions:
    if form.has_key('clearTmp'):
        helper.clearTmp(form['caseName'].value)
        pagesToRender = ['case','saveFile']
        message = "<strong>Success!</strong> All temporary files was deleted."
        messageType = "success"
if "editDescription" in actions:
    if form.has_key('Edit'):
        helper.updateFileDescription(form['filePath'].value, form['caseName'].value, form['description'].value)
        syslog.syslog("PCAP APP: EDIT2")

# generate begining of html
print "Content-Type: text/html\n\n"
# generate JS which bootstrap need to work
#print genBootstrapJS()
print genBegining('Main')
'''
for i in form.keys():
    print i + ": " + form[i].value + "  "
print '<br>'
'''

# begining of render section
print '<div class="alert alert-'+messageType+'">'+message+'</div>' if message else ""
print '<div class="row">\n'
print '<div class="col-md-12">'
print genBreadcrumb(pagesToRender, caseName, fileName)
print '<div class="col-md-12">\n'
if "default" in pagesToRender:
    print '<p> Default page </p>'
    print '<form method="post"><input type="hidden" name="pagesToRender" value="cases:aa"><input type="submit" value="Apply"></a></form> '

if "testpage" in pagesToRender:
    print "<p>testpage</p>"
    cases.render()
    # cases.addCase('testcasee','desc')

if "cases" in pagesToRender:
    cases.render()

if "case" in pagesToRender:
    showCase.render(form['caseName'].value)

if "saveFile" in pagesToRender:
    saveFile.render(form['caseName'].value)

if "showFile" in pagesToRender:
    if form.has_key('filePath'):
        showPCAPFileDetails.render(form['filePath'].value, form['caseName'].value)
    else:
        print '<div class="alert alert-warning"> <strong>Warning!</strong>Please select one file from list.</div>'
        showCase.render(form['caseName'].value)
        saveFile.render(form['caseName'].value)

if "showGraph" in pagesToRender:

    #renderGraph.render(form['filePath'].value)
    #try:
        start = form['start'].value if form.has_key('start') else ''
        end = form['end'].value if form.has_key('end') else ''
        xtics = form['xtics'].value if form.has_key('xtics') else ''
        if form.has_key('renderDetailedGraph'):
            print '<embed src="'+renderGraph.render(form['caseName'].value,form['filePath'].value, form.getlist('additionalFiles'), type = 'pdf', start = start, end = end, xtics = xtics)+'" width="100%" height="450" type="application/pdf">'
        else:
            print '<img width="800" src="'+renderGraph.render(form['caseName'].value,form['filePath'].value, form.getlist('additionalFiles'), type = 'png', start = start, end = end, xtics = xtics)+'">'
    #except CalledProcessError:
    #    print '<div class="alert alert-danger"> <strong>Error!</strong> Rendering graph Error, make sure you use right filter syntax and files contains some data.</div>'
    #    print '<div class="alert alert-info"> <strong>Info!</strong> Your filter could be also too restricted and didnt leave enough TCP packets to render graph. Try less restrictive filter.'
    # print '<img width="400" src="renderGraph.py?fileName='+form['filePath'].value+'">'
    # print '<img width="400" src="cases/case01/PCAPs/tmp/throughput.png">'


#  generate back button
print '<div class="col-md-12">'
print genBackButton(pagesToRender, form['caseName'].value) if form.has_key("caseName") else genBackButton(pagesToRender)
print '</div>'
print '</div>\n</div>'

# generate end of html
print genEnd()
