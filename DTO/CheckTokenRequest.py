#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

class CheckTokenRequest(object):
	def __init__(self, email, token):
		self.email=email.strip()
		self.token=token.strip()

	@staticmethod
	def toJson(obj):
		return json.dumps(obj.__dict__)

	@staticmethod
	def fromJson(jsonstr):
		return json.loads(jsonstr, object_hook=lambda d: CheckTokenRequest(**d))