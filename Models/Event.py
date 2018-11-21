#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from typing import List
from MusicGenre import MusicGenre

class Event(object):
	def __init__(self, id:int, name:str, ticketprice:float, minimumage:int, startdate:long, enddate:long,musicgenres:List[MusicGenre]):
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
