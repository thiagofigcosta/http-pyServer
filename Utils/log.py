#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import datetime
import socket

class Logger(object):
	def __init__(self, filename="log.txt"):
		self.filename=filename
		
	def log(self,message,error=False,traceback=False,printonscreen=True):
		now = datetime.datetime.now()
		nowstr=now.strftime("%Y%m%d-%H:%M:%S.")+'{:06d}'.format(now.microsecond)
		info_header="["+socket.gethostname()+"|"+nowstr+"] "
		fail_delimiter="***********************************************"
		error_header  ="*--------------------ERROR--------------------*"
		traceb_header ="*------------------TRACE_BACK------------------"
		formatted_message =""
		if error or traceback:
			formatted_message=info_header+'\n'+fail_delimiter+'\n'
			if error:
				formatted_message+=error_header+'\n'
			if traceback:
				formatted_message+=traceb_header+'\n'
			formatted_message+=fail_delimiter+'\n'
			formatted_message+=message+'\n'
			formatted_message+=fail_delimiter
		else:
			formatted_message=info_header+message
		if printonscreen:
			if error:
				sys.stderr.write(formatted_message+'\n')
				sys.stderr.flush()
			else:
				print (formatted_message)
		formatted_message+='\n'
		with open(self.filename, "a") as logfile:
			logfile.write(formatted_message)