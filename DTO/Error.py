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
	def toJson(error):
		return json.dumps(error.__dict__)

	@staticmethod
	def fromJson(json):
		return json.loads(json, object_hook=lambda d: Error(**d))

	@staticmethod
	def listToJson(errors):
		return "{\"errors\":"+json.dumps([error.__dict__ for error in errors])+"}"
		