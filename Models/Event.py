#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from typing import List
from MusicGenre import MusicGenre

class Event(object):
	def __init__(self, id, name, ticketprice, minimumage, startdate, enddate, musicgenres):
		self.id=id
		self.name=name
		self.ticketprice=ticketprice
		self.minimumage=minimumage
		self.startdate=startdate
		self.enddate=enddate
		self.musicgenres=musicgenres

	@staticmethod
	def toJson(event):
		return json.dumps(event.__dict__)

	@staticmethod
	def fromJson(json):
		return json.loads(json, object_hook=lambda d: Event(**d))

	@staticmethod
	def listToJson(events):
		return "{\"events\":"+json.dumps([event.__dict__ for event in events])+"}"
