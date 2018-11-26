#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

class RegisterEventRequest(object):
	def __init__(self, name, ticketprice, minimumage, startate, enddate):
		self.name=name.strip()
		self.ticketprice=ticketprice
		self.minimumage=minimumage
		self.startate=startate
		self.enddate=enddate


	@staticmethod
	def toJson(obj):
		return json.dumps(obj.__dict__)

	@staticmethod
	def fromJson(jsonstr):
		return json.loads(jsonstr, object_hook=lambda d: RegisterEventRequest(**d))
