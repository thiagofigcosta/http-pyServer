#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

class Account(object):
	def __init__(self, id:int, email:str, firstname:str, lastname:str, accesslevel:int, cpf:str, active:str, timeregistered:long):
		self.id=id
		self.email=email
		self.firstname=firstname
		self.lastname=lastname
		self.accesslevel=accesslevel
		self.cpf=cpf
		self.active=active
		self.timeregistered=timeregistered

	@staticmethod
	def toJson(account):
		if account.active!="Active":
			token=account.active
			account.active="NOPS"
			jsonstr=json.dumps(account.__dict__)
			account.active=token
			return jsonstr
		else:
			return json.dumps(account.__dict__)

	@staticmethod
	def fromJson(json):
		return json.loads(json, object_hook=lambda d: Account(**d))
