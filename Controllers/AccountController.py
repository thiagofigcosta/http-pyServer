#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

sys.path.insert(0, '../Services')

from HTTPService import HTTPType
from HTTPService import StatusCode

from MainController import Controller
from MainController import Resource


class AccountController(Controller):
	def __init__(self, sql, path):
		super(AccountController, self).__init__(sql,path)
		self.resources.append(Resource("login",HTTPType.POST))

	def handle(self,request):
		for resource in self.resources:
			if request.url.resource==resource.name and request.type==resource.type:
				login=LoginRequest.fromJson(request.data)
				securityInfo=self.sql.getAccountSecurityInfo(login.email)
				if securityInfo == None:
					error=Error(str(404),{"pointer": request.url.path+request.url.resource},"Not found","Account not found on databse.")
					return HTTP(status=StatusCode.C404,data=Error.listToJson([error]),contenttype="application/json")
				else:
					hash=pbkdf2.PBKDF2(login.password,securityInfo["salt"],666).hexread(32)
					if hash==securityInfo["hash"]:
						account=self.sql.getAccount(id=securityInfo["id"])
						return HTTP(status=StatusCode.OK,data=Account.toJson(account),contenttype="application/json")
					else:
						error=Error(str(401),{"pointer": request.url.path+request.url.resource},"Unauthorized","Incorrect email or password.")
						return HTTP(status=StatusCode.C401,data=Error.listToJson([error]),contenttype="application/json")
		error=Error(str(404),{"pointer": request.url.path+request.url.resource},"Not found","Resource not implemented on backend.")
		return HTTP(status=StatusCode.C500,data=Error.listToJson([error]),contenttype="application/json")