#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from Address import Address

class Nightclub(object):
	def __init__(self, id, name, cnpj, phone, email, address, id_account):
		self.id=id
		self.name=name
		self.cnpj=cnpj
		self.phone=phone
		self.email=email
		self.address=Address.toJson(address)
		self.id_account=id_account

	@staticmethod
	def toJson(nigthclub):
		return json.dumps(nigthclub.__dict__)
		# bkp_addr=nigthclub.address
		# nigthclub.address=None
		# jsonstr=json.dumps(nigthclub.__dict__)
		# nigthclub.address=bkp_addr
		# addr_json=Address.toJson(bkp_addr)
		# return jsonstr.replace('"address": null', '"address": '+addr_json)

	@staticmethod
	def fromJson(jsonstr):
		return json.loads(jsonstr, object_hook=lambda d: Nightclub(**d))

	@staticmethod
	def listToJson(nightclubs):
		return "{\"nightclubs\":"+json.dumps([nightclub.__dict__ for nightclub in nightclubs])+"}"