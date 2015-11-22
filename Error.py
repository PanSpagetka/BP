import os
import time
from CONSTANTS import *
from Log import *

class Error:		
	def __init__(self, description):
		self.lastError = description
		self.lastErrorOccured = None
		self.log = Log(ERROR_LOG, description)	
		
		
	def raiseError(self, description = None):
		""" write error with timestamp to ERROR_LOG file defined in CONSTANTS.py	
		
		Keyword arguments:
    		description -- description of error which occured (default self.description - last printed error description)			
		"""
		self.lastErrorOccured = time.asctime( time.localtime(time.time())) 
		if(description is None):
			self.log.logToFile()
		else:
			self.lastError = description
			self.log.logToFile(message = description)			
		
		
		