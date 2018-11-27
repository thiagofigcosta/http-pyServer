#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

sys.path.insert(0, '../DTO')
sys.path.insert(0, '../Services')

from Error import Error
from HTTPService import HTTP
from HTTPService import HTTPType
from HTTPService import StatusCode
from FeedbackRequest import FeedbackRequest


class Resource(object): # TODO assign callback to resources to not implement handle on child of Controller
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


class MainController(Controller): # TODO assign callback to resources to not implement handle on child of Controller
	def __init__(self, server, path):
		super(MainController, self).__init__(server,path)
		self.controllers=[]
		self.controllers.append(self)
		self.resources.append(Resource("feedback",HTTPType.POST))

	def appendController(self,controller):
		self.controllers.append(controller)

	def routeRequest(self,request):
		if request.data==None and request.type==HTTPType.POST:
			error=Error(str(400),{"pointer": request.url.path},"Bad Request","POST request whitout data.")
			return HTTP(status=StatusCode.C400,data=Error.listToJson([error]),contenttype="application/json")
		for controller in self.controllers:
			if request.url.path==controller.path:
				return controller.handle(request)
		error=Error(str(404),{"pointer": request.url.path},"Not found","Path url not mapped on backend.")
		return HTTP(status=StatusCode.C500,data=Error.listToJson([error]),contenttype="application/json")

	def handle(self,request):
		for resource in self.resources:
			if request.url.resource==resource.name and request.type==resource.type:
				if resource.name=="feedback":
					return self.feedback(request)

		error=Error(str(404),{"pointer": request.url.path+'/'+request.url.resource},"Not found","Resource not implemented on backend.")
		return HTTP(status=StatusCode.C500,data=Error.listToJson([error]),contenttype="application/json")

	def feedback(self,request):
		feed=FeedbackRequest.fromJson(request.data)
		self.email.SendFeedbackMail(feed.email,feed.category,feed.message)
		return HTTP(status=StatusCode.OK,data="Feedback sented, thank you.",contenttype="text/plain")