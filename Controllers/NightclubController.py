#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

sys.path.insert(0, '../DTO')
sys.path.insert(0, '../Services')

from HTTPService import HTTPType
from HTTPService import StatusCode
from HTTPService import HTTP
from Error import Error
from MainController import Controller
from MainController import Resource
from RegisterNCRequest import RegisterNCRequest

class NightclubController(Controller):
	def __init__(self, server, path):
		super(NightclubController, self).__init__(server,path)
		self.resources.append(Resource("register",HTTPType.POST))

	def handle(self,request):
		for resource in self.resources:
			if request.url.resource==resource.name and request.type==resource.type:
				if resource.name=="register":
					return self.register(request)
				
		error=Error(str(404),{"pointer": request.url.path+'/'+request.url.resource},"Not found","Resource not implemented on backend.")
		return HTTP(status=StatusCode.C500,data=Error.listToJson([error]),contenttype="application/json")

	def register(self,request):
		night=RegisterNCRequest.fromJson(request.data)
		if self.sql.checkIfAccountExists(id=night.owner_id):
			if not self.sql.checkIfNCExistsByCnpj(night.cnpj):
				addr_id=self.sql.getAddressId(night.zipcode, night.street, night.number, night.xtrainfo, night.district, night.city, night.state, night.country)
				if addr_id==None:
					self.sql.createAddress(night.zipcode, night.street, night.number, night.xtrainfo, night.district, night.city, night.state, night.country)
					addr_id=self.sql.getAddressId(night.zipcode, night.street, night.number, night.xtrainfo, night.district, night.city, night.state, night.country)
				self.sql.createNightclub(night.name, night.cnpj, night.phone, night.email, addr_id, night.owner_id)
				nightclub=self.sql.getNightclub(night.cnpj)
				return HTTP(status=StatusCode.OK,data=Nightclub.toJson(nightclub),contenttype="application/json")
			else:
				error=Error(str(401),{"pointer": request.url.path+'/'+request.url.resource},"Unauthorized","Nightclub already registered.")
				return HTTP(status=StatusCode.C401,data=Error.listToJson([error]),contenttype="application/json")
		else:
			error=Error(str(404),{"pointer": request.url.path+'/'+request.url.resource},"Not found","Account not found on databse.")
			return HTTP(status=StatusCode.C404,data=Error.listToJson([error]),contenttype="application/json")