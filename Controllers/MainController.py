#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Resource(object):
	def __init__(self, name, type):
		self.name=name
		self.type=type
		

class Controller(object):
	def __init__(self, sql, path):
		self.path=path
		self.sql=sql
		self.resources=[] # children must check resources list to handle requests

	def handle(self,request):
		pass # implement in children


class MainController(Controller):
	def __init__(self, sql, path):
		super(MainController, self).__init__(sql,path)
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
		pass