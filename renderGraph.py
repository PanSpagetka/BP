
import os, os.path, subprocess, sys, syslog, datetime, shutil, Filter, helper
from config import *

def render(caseName, filePath, additionalFiles = [], type = 'png', start = '', end = '', xtics = ''):
	syslog.syslog("PCAP APP: renderGraph: started: "+str(datetime.datetime.now()))
	colors = ["red","black", "yellow","green","blue","cyan","orange","violet"]
	originFileName = helper.getDBNameFromPath(filePath)
	dirpath = os.path.dirname(filePath) + '/tmp'

	dirpath = CASES_DIR + caseName + TMP_DIR
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
	f = helper.getFilter(caseName, helper.getDBNameFromPath(filePath))
	info = helper.getReadableFileInfo(helper.getDBNameFromPath(filePath), caseName)
	if info[4]:
		originFileName = info[4]
	syslog.syslog("PCAP APP: "+helper.getDBNameFromPath(filePath))
	plot = 'plot "'+os.path.basename(data.name)+'" using 2:4  every ::13 with lines ls 1 lc rgb "'+colors[0]+'" title "'+originFileName+", filter: "+f+'"'
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
		info = helper.getReadableFileInfo(file, caseName)
		f = helper.getFilter(caseName,file)
		if info[4] != 'n/a':
			file = info[4]
		plot += ', "'+os.path.basename(data.name)+'" using 2:4  every ::13 with lines ls 1 lc rgb "'+colors[i%8]+'" title "'+file+",filter: "+f+'"'
		data.close()
		i += 1
	script.write(plot)
	script.close()

	os.chdir(dirpath)
	if type == 'png':
		subprocess.check_output(['make','png'])
		ret = dirpath + '/throughput.png'
	else:
		subprocess.check_output(['make'])
		ret = dirpath + '/throughput.pdf'
	syslog.syslog("PCAP APP: renderGraph:   ended: "+str(datetime.datetime.now()))
	return ret
