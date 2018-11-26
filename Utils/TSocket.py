#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket

class TSocket(object):
	def __init__(self, sock):
		self.sock=sock
		#extra attributes
		sockdata=sock.getpeername()
		self.TSname=sockdata[0]+":"+str(sockdata[1])
		self.TSrunning=True

	def __getattr__(self, attr):
		if hasattr(self.sock, attr):
			def wrapper(*args, **kwargs):
				return getattr(self.sock, attr)(*args, **kwargs)
			return wrapper
		raise AttributeError(attr)

	def close(self):
		try:
			super(TSocket, self).close()
		except:
			pass
		self.TSrunning=False