#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

class FeedbackRequest(object):
	def __init__(self, email, category, message):
		self.email=email.strip()
		self.category=category.strip()
		self.message=message.strip()

	@staticmethod
	def toJson(obj):
		return json.dumps(obj.__dict__)

	@staticmethod
	def fromJson(jsonstr):
		return json.loads(jsonstr, object_hook=lambda d: FeedbackRequest(**d))