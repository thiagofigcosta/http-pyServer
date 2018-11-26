#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

class MusicGenre(object):
	def __init__(self, id, name):
		self.id=id
		self.name=name

	@staticmethod
	def toJson(musicgenre):
		return json.dumps(musicgenre.__dict__)

	@staticmethod
	def fromJson(jsonstr):
		return json.loads(jsonstr, object_hook=lambda d: MusicGenre(**d))

	@staticmethod
	def listToJson(musicgenres):
		return "{\"musicgenres\":"+json.dumps([musicgenre.__dict__ for musicgenre in musicgenres])+"}"