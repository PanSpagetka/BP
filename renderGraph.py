
import os, os.path, subprocess, sys, syslog, datetime, shutil, Filter
from config import *

#form = cgi.FieldStorage()
def render(caseName, filePath, additionalFiles = [], type = 'png', start = '', end = '', xtics = ''):
	syslog.syslog("PCAP APP: renderGraph: started: "+str(datetime.datetime.now()))
	colors = ["red","black", "yellow","green","blue","cyan","orange","violet"]
	#filepath = os.path.abspath(filePath)
	originFileName = os.path.basename(filePath)
	dirpath = os.path.dirname(filePath) + '/tmp'
	#call captcp and draw graph to png file

	#ret = subprocess.check_output(['captcp','throughput','-i','-o',dirpath,filepath])



	ret = Filter.applyTimeFilterOnFile(filePath,caseName,start,end)
	if ret:
		filePath = ret
		dirpath = os.path.dirname(filePath)

	shutil.copy(GRAPH_SCRIPT_DIR+'Makefile',dirpath)
	if type == 'png':
		shutil.copy(GRAPH_SCRIPT_DIR+'throughput.gpi',dirpath+"/"+'throughput.gpi')
	else:
		shutil.copy(GRAPH_SCRIPT_DIR+'throughputDetail.gpi',dirpath+"/"+'throughput.gpi')

	data = open(dirpath+'/'+os.path.basename(filePath)+'.data', 'w')
	syslog.syslog("PCAP APP: Processing file: "+filePath+" started: "+str(datetime.datetime.now()))
	subprocess.call(['tshark', '-q', '-nr', filePath, '-t', 'ad', '-z' 'io,stat,1'], stdout = data)
	syslog.syslog("PCAP APP: Processing file: "+filePath+"   ended: "+str(datetime.datetime.now()))
	script = open(dirpath+'/throughput.gpi', 'a')
	if xtics != '' :
		try:
			xtics = int(xtics)
			script.write("set xtics " + str(xtics) + '\n')
		except ValueError:
			pass
	plot = 'plot "'+os.path.basename(data.name)+'" using 2:4  every ::13 with lines ls 1 lc rgb "'+colors[0]+'" title "'+originFileName+'"'
	syslog.syslog("PCAP APP: " + plot)
	data.close()
	i = 1
	for file in additionalFiles:
		filePath =  CASES_DIR + caseName + PCAP_DIR + file
		ret = Filter.applyTimeFilterOnFile(filePath,caseName,start,end)
		if ret:
			filePath = ret
			dirpath = os.path.dirname(filePath)
		data = open(dirpath+'/' + file.replace('/', '-') + '.data', 'w')
		syslog.syslog("PCAP APP: Processing file: "+file+" started: "+str(datetime.datetime.now()))
		subprocess.call(['tshark', '-q', '-nr',filePath, '-t', 'ad', '-z' 'io,stat,1'], stdout = data)
		syslog.syslog("PCAP APP: Processing file: "+file+"   ended: "+str(datetime.datetime.now()))
		plot += ', "'+os.path.basename(data.name)+'" using 2:4  every ::13 with lines ls 1 lc rgb "'+colors[i%8]+'" title "'+file+'"'
		data.close()
		i += 1
	script.write(plot)
	script.close()

#  "throughput.data" using 2:4  every ::13 with lines ls 1 title 'throughput.data', \
#"data" using 2:4  every ::13 with lines ls 1 lc rgb 'gold' title 'data'



	'''cmd = ['captcp']
	cmd.append(graphType)
	cmd += graphOptions.split(" ")
	cmd.append(dirpath)
	cmd.append(filepath)
	ret = subprocess.call(cmd)'''
	os.chdir(dirpath)
	if type == 'png':
		subprocess.check_output(['make','png'])
		ret = dirpath + '/throughput.png'
	else:
		subprocess.check_output(['make'])
		ret = dirpath + '/throughput.pdf'
	syslog.syslog("PCAP APP: renderGraph:   ended: "+str(datetime.datetime.now()))
	return ret
	'''
	img = open(path + '/throughput.png', 'rb')
	print 'Content-type: image/png'
	print
	print img.read()
	img.close()'''
	'''
if form.has_key('filePath'):
	filepath = os.path.abspath(form['filePath'].value)
	dirpath = os.path.dirname(filepath) + '/tmp'

	#call captcp and draw graph to png file

	ret = subprocess.check_output(['captcp','throughput','-i','-o',dirpath,filepath])
	print 'ret: ' + ret
	os.chdir(dirpath)
	ret = subprocess.check_output(['make','png'])
	print 'ret: ' + ret
	#load image from file and print it binary
	path = os.getcwd()
	img = open(path + '/throughput.png', 'rb')
	print 'Content-type: image/png'
	print
	print img.read()
	img.close()
'''
'''

#!/usr/bin/python

import cgi
import cgitb
import os, os.path, subprocess
from htmlGen import *
from config import *
cgitb.enable()

form = cgi.FieldStorage()


if form.has_key('filename'):
	filepath = os.path.abspath(form['filename'].value)
	dirpath = os.path.dirname(filepath) + '/tmp'

	#call captcp and draw graph to png file
	ret = subprocess.check_output(['captcp','throughput','-i','-o',dirpath,filepath])
	os.chdir(dirpath)
	ret = subprocess.check_output(['make','png'])

	#load image from file and print it binary
	path = os.getcwd()
	img = open(path + '/throughput.png', 'rb')
	print 'Content-type: image/png'
	print
	print img.read()
	img.close()
'''
	#tohle funguje
	#print '<img width="800" src="'+CASES_DIR+form['casename'].value+TMP_DIR+'throughput.png">'

#print genEnd()
'''
if 'case' in form:
	path = os.getcwd()
	path += '/cases/'+form['case'].value +'/img.png'
	if os.path.isfile(path):
		img = open(path, "rb")
		#print 'Content-type: image/png \n'
		print img.read()
		img.close()
	else:
		path = os.getcwd()
		path += '/img/error.png'
		img = open(path, "rb")
		print img.read()
		img.close()
else:
	img = open("./img/error.png", "rb")
	#print 'Content-type: image/png \n'
	print img.read()
	img.close()

'''
