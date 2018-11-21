#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import json
from enum import Enum

class StatusCode(Enum):
	OK=200

class HTTPType(Enum):
	Response=64313
	GET=91603
	POST=514320


class HTTP(object):
	def __init__(self, requestdata:str):
		lines=requestdata.split('\n')
		rawfields={}
		httpandversion=False
		requesttype=False
		readingdata=False

		for line in lines:
			if httpandversion==requesttype==False:
				idxOfHttp=line.find("HTTP")
				linesize=len(requestdata)
				if idxOfHttp>0:
					tmp_version=""
					for i in xrange(idxOfHttp+len("HTTP"),linesize):
						currentchar=line[i]
						if (currentchar>'0' and currentchar<'9') or currentchar=='.' or currentchar==',':
							tmp_version+=currentchar
						elif tmp_version!="":
							break
					if tmp_version!="":
						self.version=int(tmp_version)
						httpandversion=True
					else:
						print ("erro") # TODO

					if "GET" in line:
						self.type=HTTPType.GET
						requesttype=True
					elif "POST" in line:
						self.type=HTTPType.POST
						requesttype=True
					else:
						print ("erro") # TODO
			elif httpandversion==requesttype==True and not readingdata:
				if line=="":
					readingdata=True
				else:
					idxOfSeparator=line.find(":")
					if idxOfSeparator>0:
						rawfields[line[:idxOfSeparator].strip()]=line[(idxOfSeparator+1):].sptrip()
			elif httpandversion==requesttype==True and readingdata:
				self.data+=line+'\n'

		if len(rawfields)>0: 
			# TODO, atribuir dados do dicionario às variaveis self


		def toString() -> str:
			# TODO


	def __init__(self, status:StatusCode=StatusCode.OK, contenttype:str=None, body:str=None):
		self.type=HTTPType.Response
		self.status=status
		self.contenttype=contenttype
		self.body=body
		self.version=1.1
		self.server="nanoTech Pure HTTP PyServer - "+socket.gethostname()

	@staticmethod
	def toJson(http):
		return json.dumps(http.__dict__)

	@staticmethod
	def fromJson(json):
		return json.loads(json, object_hook=lambda d: HTTP(**d))
