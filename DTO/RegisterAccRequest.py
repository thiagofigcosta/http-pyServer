#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

class RegisterAccRequest(object):
	def __init__(self, firstname, lastname, cpf, email, password, accesslevel=3):
		self.firstname=firstname.strip()
		self.lastname=lastname.strip()
		self.cpf=cpf.strip()
		self.email=email.strip()
		self.password=password.strip()
		self.accesslevel=accesslevel

	@staticmethod
	def toJson(obj):
		return json.dumps(obj.__dict__)

	@staticmethod
	def fromJson(jsonstr):
		return json.loads(jsonstr, object_hook=lambda d: RegisterAccRequest(**d))
