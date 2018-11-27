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
from RegisterNCRequest import RegisterNCRequest
from Nightclub import Nightclub

class NightclubController(Controller):
	def __init__(self, server, path):
		super(NightclubController, self).__init__(server,path)
		self.resources.append(Resource("register",HTTPType.POST))
		self.resources.append(Resource("get",HTTPType.GET))
		self.resources.append(Resource("all",HTTPType.GET))
		self.resources.append(Resource("owner",HTTPType.GET))

	def handle(self,request):
		for resource in self.resources:
			if request.url.resource==resource.name and request.type==resource.type:
				if resource.name=="register":
					return self.register(request)
				elif resource.name=="get":
					return self.get(request)
				elif resource.name=="all":
					return self.getAll(request)
				elif resource.name=="owner":
					return self.getAllByOwner(request)
				
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

	def get(self,request):
		night=self.sql.getNightclubById(request.url.query)
		if night!=None:
			return HTTP(status=StatusCode.OK,data=Nightclub.toJson(night),contenttype="application/json")
		error=Error(str(404),{"pointer": request.url.path+'/'+request.url.resource},"Not found","Nightclub not found on databse.")
		return HTTP(status=StatusCode.C404,data=Error.listToJson([error]),contenttype="application/json")

	def getAll(self, request):
		clubs=self.sql.getNightclubs()
		return HTTP(status=StatusCode.OK,data=Nightclub.listToJson(clubs),contenttype="application/json")

	def getAllByOwner(self, request):
		clubs=self.sql.getNightclubsByOwner(request.url.query)
		return HTTP(status=StatusCode.OK,data=Nightclub.listToJson(clubs),contenttype="application/json")