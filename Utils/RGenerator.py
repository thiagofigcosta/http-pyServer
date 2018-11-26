#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import time

class RGenerator(object):	
	def genSalt(size=64):
		random.seed(time.time())
		ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
		chars=[]
		for i in range(size):
		    chars.append(random.choice(ALPHABET))
		return ''.join(chars)

	def genToken(size=5):
		random.seed(time.time())
		ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
		chars=[]
		for i in range(size):
		    chars.append(random.choice(ALPHABET))
		return ''.join(chars)