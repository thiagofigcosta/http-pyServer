#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

class LoginRequest(object):
	def __init__(self, email, password, uuid):
		self.email=email
		self.password=password
		self.uuid=uuid

	@staticmethod
	def toJson(login):
		return json.dumps(login.__dict__)

	@staticmethod
	def fromJson(jsonstr):
		return json.loads(jsonstr, object_hook=lambda d: LoginRequest(**d))

		