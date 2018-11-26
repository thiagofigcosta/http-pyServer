#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

class RegisterNCRequest(object):
	def __init__(self, name, email, zipcode, street, number, xtrainfo, district, city, state, country, phone, cnpj, owner_id):
		self.name=name.strip()
		self.email=email.strip()
		self.zipcode=zipcode
		self.street=street.strip()
		self.number=number
		self.xtrainfo=xtrainfo.strip()
		self.district=district.strip()
		self.city=city.strip()
		self.state=state.strip()
		self.country=country.strip()
		self.phone=phone.strip()
		self.cnpj=cnpj
		self.owner_id=owner_id


	@staticmethod
	def toJson(obj):
		return json.dumps(obj.__dict__)

	@staticmethod
	def fromJson(jsonstr):
		return json.loads(jsonstr, object_hook=lambda d: RegisterNCRequest(**d))
