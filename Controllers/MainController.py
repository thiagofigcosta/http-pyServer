#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

sys.path.insert(0, '../DTO')
sys.path.insert(0, '../Services')

from Error import Error
from HTTPService import HTTP
from HTTPService import StatusCode


class Resource(object):
	def __init__(self, name, type):
		self.name=name
		self.type=type
		

class Controller(object):
	def __init__(self, server, path):
		self.path=path
		self.sql=server.sql
		self.email=server.email
		self.resources=[] # children must check resources list to handle requests

	def handle(self,request):
		pass # implement in children


class MainController(Controller):
	def __init__(self, server, path):
		super(MainController, self).__init__(server,path)
		self.controllers=[]
		self.controllers.append(self)

	def appendController(self,controller):
		self.controllers.append(controller)

	def routeRequests(self,request):
		for controller in self.controllers:
			if request.url.path==controller.path:
				return controller.handle(request)
		error=Error(str(404),{"pointer": request.url.path},"Not found","Path url not mapped on backend.")
		return HTTP(status=StatusCode.C500,data=Error.listToJson([error]),contenttype="application/json")

	def handle(self,request):
		error=Error(str(404),{"pointer": request.url.path+'/'+request.url.resource},"Not found","Resource not implemented on backend.")
		return HTTP(status=StatusCode.C500,data=Error.listToJson([error]),contenttype="application/json")