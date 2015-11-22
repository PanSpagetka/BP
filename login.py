#!/usr/bin/python

import cgi
import cgitb,os
from htmlGen import *
from User import *

cgitb.enable()

# generate begining of html
print "Content-Type: text/html\n\n"
print genBegining('Login')

# check login
print ' <form method="post" action="checkLogin.py">Username:<br><input type="text" name="username"><br>Password:<br><input type="password" name="password"><br><br><input type="submit" value="Login"></form> '

# if error occured print it
form = cgi.FieldStorage()
if(form.has_key('error')):
	print form['error'].value


# generate end of html
print genEnd()



#print "Content-Type: text/html Set-Cookie:UserID=XxYZ; Set-Cookie:LoggedIn=false;\r\n"

#print genHref("?action=print")

'''
if "HTTP_COOKIE" in os.environ:
    print os.environ["HTTP_COOKIE"]
else:
    print "HTTP_COOKIE not set!"'''

'''
users = loadFromFile('Users.db')
form = cgi.FieldStorage()
if (form.has_key("username") and form.has_key("password")):
	if(form["username"].value in users and users[form["username"].value].password == form["password"].value):
		url = "test.py"
		print "Status: 302 Moved"
		print "Location: %s" % url
		print
	else:
		print "Bad username or password

'''