#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

class RegisterEventRequest(object):
	def __init__(self, name, ticketprice, minimumage, startdate, enddate, club_id, mgenreslist):
		self.name=name.strip()
		self.ticketprice=ticketprice
		self.minimumage=minimumage
		self.startdate=startdate
		self.enddate=enddate
		self.club_id=club_id
		self.mgenreslist=mgenreslist


	@staticmethod
	def toJson(obj):
		return json.dumps(obj.__dict__)

	@staticmethod
	def fromJson(jsonstr):
		return json.loads(jsonstr, object_hook=lambda d: RegisterEventRequest(**d))
