#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from MusicGenre import MusicGenre

class Event(object):
	def __init__(self, id, name, ticketprice, minimumage, startdate, enddate, musicgenres, nightclub_id):
		self.id=id
		self.name=name
		self.ticketprice=ticketprice
		self.minimumage=minimumage
		self.startdate=startdate
		self.enddate=enddate
		self.musicgenres=MusicGenre.listToJson(musicgenres)
		self.nightclub_id=nightclub_id

	@staticmethod
	def toJson(event):
		return json.dumps(event.__dict__)

	@staticmethod
	def fromJson(jsonstr):
		return json.loads(jsonstr, object_hook=lambda d: Event(**d))

	@staticmethod
	def listToJson(events):
		return "{\"events\":"+json.dumps([event.__dict__ for event in events])+"}"
