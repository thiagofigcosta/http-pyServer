#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

class ResetPasswordRequest(object):
	def __init__(self, email, token, newpassword):
		self.email=email.strip()
		self.token=token.strip()
		self.newpassword=newpassword.strip()

	@staticmethod
	def toJson(obj):
		return json.dumps(obj.__dict__)

	@staticmethod
	def fromJson(jsonstr):
		return json.loads(jsonstr, object_hook=lambda d: ResetPasswordRequest(**d))