#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

class RegisterAccRequest(object):
	def __init__(self, firstname, lastname, cpf, email, password):
		self.firstname=firstname.strip()
		self.lastname=lastname.strip()
		self.cpf=cpf.strip()
		self.email=email.strip()
		self.password=password.strip()

	@staticmethod
	def toJson(register):
		return json.dumps(register.__dict__)

	@staticmethod
	def fromJson(jsonstr):
		return json.loads(jsonstr, object_hook=lambda d: RegisterAccRequest(**d))
