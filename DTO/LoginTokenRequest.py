#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

class LoginTokenRequest(object):
	def __init__(self, email, uuid, timestamp):
		self.email=email.strip()
		self.uuid=uuid.strip()
		self.timestamp=timestamp

	@staticmethod
	def toJson(obj):
		return json.dumps(obj.__dict__)

	@staticmethod
	def fromJson(jsonstr):
		return json.loads(jsonstr, object_hook=lambda d: LoginTokenRequest(**d))