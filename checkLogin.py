#!/usr/bin/python

import cgi
import cgitb
from htmlGen import *
from User import *


cgitb.enable()


#print genHref("?action=print")
#print "Set-Cookie:LoggedIn=true;\r\n"
#environ['LoggedIn'] = 'true'


form = cgi.FieldStorage()
if (form.has_key("username") and form.has_key("password")):
	users = loadFromFile('Users.db')
	if(form["username"].value in users and users[form["username"].value].password == form["password"].value):
		url = "cases.py"
		print "Status: 302 Moved"
		print "Location: %s" % url
		print
	else:
		url = "login.py?error=badPasswordOrUsername"
		print "Status: 302 Moved"
		print "Location: %s" % url
		print



