#!/usr/bin/python

import cgi
from htmlGen import *

print "Content-Type: text/html\n\n"
print genBegining('test')
#print "<img width=\"100\" src=\"renderGraph.py?graphType=pcap&from=1.1.&to=2.2.\">"
#print "<img width=\"100\" src=\"renderGraph.py?case=case02\">"
#print '<img width="100" src="renderGraph.py?case='+case.casename+'">'
#print '<p><a href="?action=print">test</a></p>'
print genHref("?action=print")

print '<form method="get"><input type="text" name="caseName"><input type="text" name="caseDescription"><input type="submit"></form>'

form = cgi.FieldStorage()
if (form.has_key("caseName") and form.has_key("caseDescription")):
	print "Case name: " + form["caseName"].value
	print "Case description: " + form["caseDescription"].value

print form["action"].value
print genEnd()


