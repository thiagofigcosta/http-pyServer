#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

sys.path.insert(0, '../DTO')
sys.path.insert(0, '../Models')
sys.path.insert(0, '../Services')

from HTTPService import HTTPType
from HTTPService import StatusCode
from HTTPService import HTTP
from Error import Error
from MainController import Controller
from MainController import Resource
from MusicGenre import MusicGenre


class MusicgenreController(Controller):
	def __init__(self, server, path):
		super(MusicgenreController, self).__init__(server,path)
		self.resources.append(Resource("all",HTTPType.GET))

	def handle(self,request):
		for resource in self.resources:
			if request.url.resource==resource.name and request.type==resource.type:
				if resource.name=="all":
					return self.getAll(request)
				
		error=Error(str(404),{"pointer": request.url.path+'/'+request.url.resource},"Not found","Resource not implemented on backend.")
		return HTTP(status=StatusCode.C500,data=Error.listToJson([error]),contenttype="application/json")

	def getAll(self,request):
		genres=self.sql.getMusicgenres()
		return HTTP(status=StatusCode.OK,data=MusicGenre.listToJson(genres),contenttype="application/json")
