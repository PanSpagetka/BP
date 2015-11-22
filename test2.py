from htmlGen import *
from Case import *
from User import *
import os
from CONSTANTS import *
from Log import *
from Error import *

def render():
	print "test2****"

'''
path = 'home/tmp/file.pcp'
filename = os.path.basename(path).split('.')
print path
print filename[0]



e = Error('errr')
e.raiseError()
e.raiseError()
e.raiseError('errr2')
e.raiseError()
'''
'''
l = Log(ERROR_LOG, "test")
l.logToFile()
l.logToFile(ERROR_LOG, 'test2')
print ERROR_LOG
'''

'''
case = Case('case01','popisek')
#print genHref('link.html', 'text')
print '<img width="100" src="renderGraph.py?case='+case.casename+'">'
print "<img width=\"100\" src=\"renderGraph.py?case=case01\">"
'''

'''
cases = loadFromFile('Cases.db')

file = open('Users.db',"r")
for line in file:
	print "1"
	parts = line.split()
	users.append(User(parts[0], parts[1]))

for case in cases:
	print case + " " + cases[case].description

#print cases['case01'].casename + " " +cases['case01'].description


myUser = User('pepa','aaa')
users = loadFromFile('Users.db')
#myUser = users['pepa']
#print myUser.username
if myUser.username in users:
	print 'true'
'''
