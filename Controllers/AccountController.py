#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

sys.path.insert(0, '../DTO')
sys.path.insert(0, '../Services')
sys.path.insert(0, '../Utils')
sys.path.insert(0, '../Models')

from HTTPService import HTTPType
from HTTPService import StatusCode
from HTTPService import HTTP
from Error import Error
from MainController import Controller
from MainController import Resource
from LoginRequest import LoginRequest
from RegisterAccRequest import RegisterAccRequest
from pbkdf2 import PBKDF2
from RGenerator import RGenerator
from CheckTokenRequest import CheckTokenRequest
from ResetPasswordRequest import ResetPasswordRequest
from LoginTokenRequest import LoginTokenRequest
from Account import Account

class AccountController(Controller):
	def __init__(self, server, path):
		super(AccountController, self).__init__(server,path)
		self.CONSTANTHASHSTR="Now I am become Death, the destroyer of worlds."
		self.resources.append(Resource("login",HTTPType.POST))
		self.resources.append(Resource("logintk",HTTPType.POST))
		self.resources.append(Resource("register",HTTPType.POST))
		self.resources.append(Resource("resendtk",HTTPType.GET))
		self.resources.append(Resource("cktoken",HTTPType.POST))
		self.resources.append(Resource("forgotpwd",HTTPType.GET))
		self.resources.append(Resource("logout",HTTPType.GET))
		self.resources.append(Resource("resetpwd",HTTPType.POST))

	def handle(self,request):
		for resource in self.resources:
			if request.url.resource==resource.name and request.type==resource.type:
				if resource.name=="login":
					return self.login(request)
				if resource.name=="logintk":
					return self.loginWithToken(request)
				elif resource.name=="register":
					return self.register(request)
				elif resource.name=="resendtk":
					return self.resendToken(request)
				elif resource.name=="cktoken":
					return self.checkToken(request)
				elif resource.name=="forgotpwd":
					return self.forgotPassword(request)
				elif resource.name=="logout":
					return self.logout(request)
				elif resource.name=="resetpwd":
					return self.resetPassword(request)
				
		error=Error(str(404),{"pointer": request.url.path+'/'+request.url.resource},"Not found","Resource not implemented on backend.")
		return HTTP(status=StatusCode.C500,data=Error.listToJson([error]),contenttype="application/json")


	def login(self,request):
		login=LoginRequest.fromJson(request.data)
		securityInfo=self.sql.getAccountSecurityInfo(login.email)
		if securityInfo == None:
			error=Error(str(404),{"pointer": request.url.path+'/'+request.url.resource},"Not found","Account not found on databse.")
			return HTTP(status=StatusCode.C404,data=Error.listToJson([error]),contenttype="application/json")
		else:
			hash=PBKDF2(login.password,securityInfo["salt"],666).hexread(32)
			if hash==securityInfo["hash"]:
				account=self.sql.getAccount(id=securityInfo["id"])
				if account.active=="Active":
					logintoken=PBKDF2(login.email+login.uuid+str(login.timestamp)+self.CONSTANTHASHSTR,login.uuid+str(login.timestamp)+self.CONSTANTHASHSTR,666).hexread(32)
					self.sql.setLoginToken(login.email,logintoken)
					return HTTP(status=StatusCode.OK,data=Account.toJson(account),contenttype="application/json")
				else:
					error=Error(str(401),{"pointer": request.url.path+'/'+request.url.resource},"Unauthorized","Unactivated account.")
					return HTTP(status=StatusCode.C401,data=Error.listToJson([error]),contenttype="application/json")
			else:
				error=Error(str(401),{"pointer": request.url.path+'/'+request.url.resource},"Unauthorized","Incorrect email or password.")
				return HTTP(status=StatusCode.C401,data=Error.listToJson([error]),contenttype="application/json")

	def loginWithToken(self,request):
		login=LoginTokenRequest.fromJson(request.data)
		securityInfo=self.sql.getUserSecurityInfo(login.email)
		if securityInfo != None:
			logintoken=PBKDF2(login.email+login.uuid+login.timestamp+self.CONSTANTHASHSTR,login.uuid+login.timestamp+self.CONSTANTHASHSTR,666).hexread(32)
			if logintoken==securityInfo["logintoken"]:
				account=self.sql.getAccount(id=securityInfo["id"])
				return HTTP(status=StatusCode.OK,data=Account.toJson(account),contenttype="application/json")
			else:
				self.sql.setLoginToken(email,'FailedToCheck')
				error=Error(str(401),{"pointer": request.url.path+'/'+request.url.resource},"Unauthorized","Device not authorized to login with token.")
				return HTTP(status=StatusCode.C401,data=Error.listToJson([error]),contenttype="application/json")
		else:
				self.sql.setLoginToken(email,'ScrInfoNone')
				error=Error(str(404),{"pointer": request.url.path+'/'+request.url.resource},"Not found","Account token not found on databse.")
				return HTTP(status=StatusCode.C404,data=Error.listToJson([error]),contenttype="application/json")

	def register(self,request):
		register=RegisterAccRequest.fromJson(request.data)
		if not self.sql.checkIfAccountExists(email=register.email):
			salt=RGenerator.genSalt()
			hash=PBKDF2(register.password,salt,666).hexread(32)
			token=RGenerator.genToken()
			self.sql.createAccount(register.email,hash,salt,register.firstname,register.lastname,register.accesslevel,register.cpf,token)
			self.email.SendConfirmationMail(register.email,token)
			return HTTP(status=StatusCode.OK,data="Account created, please activate it.",contenttype="text/plain")
		else:
			error=Error(str(401),{"pointer": request.url.path+'/'+request.url.resource},"Unauthorized","Account already registered.")
			return HTTP(status=StatusCode.C401,data=Error.listToJson([error]),contenttype="application/json")

	def resendToken(self,request):
		email=request.url.query.strip()
		token=RGenerator.genToken()
		self.sql.updateAccountToken(email=email,token=token)
		self.email.SendConfirmationMail(email,token)
		return HTTP(status=StatusCode.OK,data="Token resented.",contenttype="text/plain")

	def checkToken(self,request):
		cktoken=CheckTokenRequest.fromJson(request.data)
		acc=self.sql.getAccount(email=cktoken.email)
		if acc.active==cktoken.token:
			self.sql.updateAccountToken(email=cktoken.email,token="Active")
			return HTTP(status=StatusCode.OK,data="Account activated.",contenttype="text/plain")
		else:
			error=Error(str(401),{"pointer": request.url.path+'/'+request.url.resource},"Unauthorized","Incorrect token.")
			return HTTP(status=StatusCode.C401,data=Error.listToJson([error]),contenttype="application/json")

	def forgotPassword(self,request):
		email=request.url.query.strip()
		if self.sql.checkIfAccountExists(email=email):
			token=self.sql.getRenewPassToken(email=email)
			if token==None:
				token=RGenerator.genToken(10);
				self.sql.setRenewPassToken(request.client,token,email=email)
				self.email.SendRenewMail(email,token)
				return HTTP(status=StatusCode.OK,data="Account already has a token, resending it.",contenttype="text/plain")
			else:
				self.email.SendRenewMail(email,token)
				error=Error(str(403),{"pointer": request.url.path+'/'+request.url.resource},"Forbidden","Account already has an active token.")
				return HTTP(status=StatusCode.C403,data=Error.listToJson([error]),contenttype="application/json")
		else:
			error=Error(str(404),{"pointer": request.url.path+'/'+request.url.resource},"Not found","Account not found on databse.")
			return HTTP(status=StatusCode.C404,data=Error.listToJson([error]),contenttype="application/json")

	def logout(self,request):
		email=request.url.query.strip()
		self.sql.setLoginToken(login.email,"")
		return HTTP(status=StatusCode.OK,data="Good bye.",contenttype="text/plain")

	def resetPassword(self,request):
		reset=ResetPasswordRequest.fromJson(request.data)
		token_sys=self.sql.getRenewPassToken(email=reset.email)
		if token_sys!=None:
			if token_sys==reset.token:
				salt=RGenerator.genSalt()
				hash=PBKDF2(reset.newpassword,salt,666).hexread(32)
				modifier=request.client
				self.sql.updateAccountPassword(hash,salt,email=reset.email)
				self.sql.disableRenewPassToken(modifier,email=reset.email)
				return HTTP(status=StatusCode.OK,data="Password renewed.",contenttype="text/plain")
			else:
				error=Error(str(401),{"pointer": request.url.path+'/'+request.url.resource},"Unauthorized","Wrong token.")
				return HTTP(status=StatusCode.C401,data=Error.listToJson([error]),contenttype="application/json")
		else:
			error=Error(str(404),{"pointer": request.url.path+'/'+request.url.resource},"Not found","Account or token not found on databse.")
			return HTTP(status=StatusCode.C404,data=Error.listToJson([error]),contenttype="application/json")