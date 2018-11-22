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

#criar classe para url de request, para reparar host, port, path, hash, e ?

class URL(object):
	def __init__(self, rawurl):
		self.protocol=None 	# first part until '://'
		self.domain=None 	# after '://'
		self.port=None 		# after ':'
		self.path=None 		# first string before the last '/'
		self.resource=None 	# last string after the last '/'
		self.query=None 	# after '?'
		self.fragment=None 	# after '#'

		# Decode url hex chars %FF

		idx=rawurl.find("://")
		if idx>0:
			self.protocol=rawurl[:idx].lower()
			rawurl=rawurl[idx+len("://"):]
		else:
			self.protocol="http" #default	
		idx=rawurl.find(":")
		if idx>0:
			self.domain=rawurl[:idx].lower()
			rawurl=rawurl[idx+len(":"):]
			idx=rawurl.find("/")
			self.port=int(rawurl[:idx])
			rawurl=rawurl[idx+len(":"):]
		else:
			self.port=80 #default
			idx=rawurl.find("/")
			if idx>0:
				self.domain=rawurl[:idx].lower() #really the domain?
				rawurl=rawurl[idx+len("/"):]
			else:
				self.domain="." #default ?

		hasQuery="?" in rawurl
		hasFragment="#" in rawurl
		rawurl=rawurl.strip()
		if hasQuery and hasFragment:
			idx=rawurl.find("#")
			if idx>0:
				self.fragment=rawurl[idx+1:]
				rawurl=rawurl[:idx+len("#")-1]
			if rawurl[len(rawurl)-1]=='/':
				rawurl=rawurl[:len(rawurl)-1]
			idx=rawurl.find("?")
			if idx>0:
				self.query=rawurl[idx+1:]
				rawurl=rawurl[:idx+len("?")-1]
			lidx=rawurl.rfind('/')
			self.path=rawurl[:lidx]
			self.resource=rawurl[lidx+1:]

		if hasQuery and not hasFragment:
			idx=rawurl.find("?")
			if idx>0:
				self.query=rawurl[idx+1:]
				rawurl=rawurl[:idx+len("?")-1]
			lidx=rawurl.rfind('/')
			if rawurl[len(rawurl)-1]=='/':
				rawurl=rawurl[:len(rawurl)-1]
			lidx=rawurl.rfind('/')
			self.path=rawurl[:lidx]
			self.resource=rawurl[lidx+1:]

		if not hasQuery and hasFragment:
			idx=rawurl.find("#")
			if idx>0:
				self.query=rawurl[idx+1:]
				rawurl=rawurl[:idx+len("#")-1]
			if rawurl[len(rawurl)-1]=='/':
				rawurl=rawurl[:len(rawurl)-1]
			lidx=rawurl.rfind('/')
			self.path=rawurl[:lidx]
			self.resource=rawurl[lidx+1:]

		if not hasQuery and not hasFragment:
			if rawurl[len(rawurl)-1]=='/':
				rawurl=rawurl[:len(rawurl)-1]
			lidx=rawurl.rfind('/')
			self.path=rawurl[:lidx]
			self.resource=rawurl[lidx+1:]

class HTTP(object):
	def __init__(self, requestdata=None, status=None, data=None, contenttype=None):
		if requestdata and not status and not data and not contenttype:
			self.type=None
			self.url=None
			self.version=None
			self.data=None
			self.useragent=None
			self.contenttype=None
			self.contentlength=None
			self.host=None
			self.accept=None
			self.acceptlanguage=None
			self.acceptencoding=None
			self.connection=None
			self.status=None
			self.server=None

			lines=requestdata.split('\n')
			nlines=len(lines)
			httpHeader=False
			blankSpace=False # https://www.youtube.com/watch?v=e-ORhEE9VVg
			for i in range(nlines):
				line=lines[i]
				if not httpHeader:
					if "HTTP" in line:
						method, url, version=line.split(' ')
						if "GET" in method:
							self.type=HTTPType.GET
							requesttype=True
						elif "POST" in method:
							self.type=HTTPType.POST
							requesttype=True
						else:
							print ("erro") # TODO
						self.url=URL(url)
						self.version=float(version.split('/')[1])
						httpHeader=True

				elif not blankSpace:
					if line=="" and self.type==HTTPType.POST:
						blankSpace=True
						self.data=""
					else:
						idxOfSeparator=line.find(":")
						if idxOfSeparator>0:
							field=line[:idxOfSeparator].strip()
							value=line[(idxOfSeparator+1):].strip()
							if field=="User-Agent":
								self.useragent=value
							elif field=="Content-Type":
								self.contenttype=value
							elif field=="Content-Length":
								self.contentlength=value
							elif field=="Host":
								self.host=value
							elif field=="Accept":
								self.accept=value
							elif field=="Accept-Language":
								self.acceptlanguage=value
							elif field=="Accept-Enconding":
								self.acceptencoding=value
							elif field=="Connection":
								self.connection=value
							else:
								print ("Unimplemented field: "+field)
				else:
					self.data+=line+'\n'
		elif not requestdata:
			self.url=None
			self.useragent=None
			self.contentlength=None
			self.host=None
			self.accept=None
			self.acceptlanguage=None
			self.acceptencoding=None
			self.connection=None

			self.type=HTTPType.Response
			self.status=status
			self.contenttype=contenttype
			self.data=data
			self.version=1.1
			self.server="nanoTech Pure HTTP PyServer - "+socket.gethostname()
		else:
			print ("erro") # TODO


	def toString():
		# TODO fazer metodo para gerar string do request a partir das variaveis de self disponiveis
		pass

	@staticmethod
	def toJson(http):
		return json.dumps(http.__dict__)

	@staticmethod
	def fromJson(json):
		return json.loads(json, object_hook=lambda d: HTTP(**d))


url=URL("http://localhost:60464/api/student?age=15")
http=HTTP("""
POST http://localhost:60464/api/student?age=15 HTTP/1.1
User-Agent: Fiddler
Host: localhost:60464
Content-Type: application/json
Content-Length: 13lines=reque

{
  id:1,
  name:'Steve'
}
""")