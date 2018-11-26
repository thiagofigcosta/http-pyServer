#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

class Error(object):
	def __init__(self, status, source, title, detail):
		self.status=status
		self.source=source
		self.title=title
		self.detail=detail

	@staticmethod
	def toJson(obj):
		return json.dumps(obj.__dict__)

	@staticmethod
	def fromJson(jsonstr):
		return json.loads(jsonstr, object_hook=lambda d: Error(**d))

	@staticmethod
	def listToJson(errors):
		return "{\"errors\":"+json.dumps([error.__dict__ for error in errors])+"}"
		