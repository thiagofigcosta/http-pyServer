#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

class Address(object):
	def __init__(self, id, zipcode, street, number, xtrainfo, district, city, state, country):
		self.id=id
		self.zipcode=zipcode
		self.street=street
		self.number=number
		self.xtrainfo=xtrainfo
		self.district=district
		self.city=city
		self.state=state
		self.country=country

	@staticmethod
	def toJson(address):
		return json.dumps(address.__dict__)

	@staticmethod
	def fromJson(json):
		return json.loads(json, object_hook=lambda d: Address(**d))
