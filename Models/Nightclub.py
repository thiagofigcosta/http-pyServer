#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from Address import Address

class Nigthclub(object):
	def __init__(self, id:int, name:str, cnpj:str, phone:str, email:str, address:Address):
		self.id=id
		self.name=name
		self.cnpj=cnpj
		self.phone=phone
		self.email=email
		self.address=address

	@staticmethod
	def toJson(nigthclub):
		return json.dumps(nigthclub.__dict__)

	@staticmethod
	def fromJson(json):
		return json.loads(json, object_hook=lambda d: Nigthclub(**d))
