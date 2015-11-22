import os
import time, sys
from CONSTANTS import *

class Log:
	def __init__(self, file, message):
		self.file = file
		self.message = message
		self.time = localtime = time.asctime( time.localtime(time.time()) )

	def logToFile(self, file = None, message = None):
		""" write message with timestamp to log file
		Format: 
			message;timestamp			
		Keyword arguments:
    		message -- message which will be written (default self.message - last printed message)
	   	 	file -- file into which will be written  (default self.file - last printed file)			
		"""
		if(message is None):
			message = self.message
		else:
			self.message = message
		if(file is None):
			file = self.file
		else:
			self.file = file
		# print message to file with timestamp 
		try:
			f = open(file, 'a')
			message += ";" + self.time + '\n'
			f.write(message)
			f.close()
		# if IOError occured print error in ERRORLOG file defined in CONSTANTS.py
		except IOError as (errno, strerror):
			f = open(ERROR_LOG,'a')
			message += "I/O error({0}): {1}".format(errno, strerror) + '\n'
			f.write(message)
			f.close()