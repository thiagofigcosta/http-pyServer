#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

class Nigthclub(object):
	def __init__(self, id, name, cnpj, phone, email, address, id_account):
		self.id=id
		self.name=name
		self.cnpj=cnpj
		self.phone=phone
		self.email=email
		self.address=address
		self.id_account=id_account

	@staticmethod
	def toJson(nigthclub):
		return json.dumps(nigthclub.__dict__)

	@staticmethod
	def fromJson(jsonstr):
		return json.loads(jsonstr, object_hook=lambda d: Nigthclub(**d))

	@staticmethod
	def listToJson(nigthclubs):
		return "{\"nigthclubs\":"+json.dumps([nigthclub.__dict__ for nigthclub in nigthclubs])+"}"