#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import socket
import json
from datetime import datetime




class HiddenStatusCode(object):
	def __init__(self, code, name):
		self.code=code
		self.name=name

class StatusCode(object):
	C100=CONTINUE=HiddenStatusCode(100,'Continue')
	C101=SWITCHING=HiddenStatusCode(101,'Switching Protocols')
	C200=OK=HiddenStatusCode(200,'OK')
	C201=CREATED=HiddenStatusCode(201,'Created')
	C202=ACCEPTED=HiddenStatusCode(202,'Accepted')
	C203=NAUTHINFO=HiddenStatusCode(203,'Non-Authoritative Information')
	C204=NCONTENT=HiddenStatusCode(204,'No Content')
	C205=RCONTENT=HiddenStatusCode(205,'Reset Content')
	C206=PCONTENT=HiddenStatusCode(206,'Partial Content')
	C300=MULTICHOICES=HiddenStatusCode(300,'Multiple Choices')
	C301=MOVED4EVER=HiddenStatusCode(301,'Moved Permanently')
	C302=FOUND=HiddenStatusCode(302,'Found')
	C303=SEEOTHER=HiddenStatusCode(303,'See Other')
	C304=NMODIFIED=HiddenStatusCode(304,'Not Modified')
	C305=USEPROXY=HiddenStatusCode(305,'Use Proxy')
	C307=TMPREDIRECTED=HiddenStatusCode(307,'Temporary Redirect')
	C400=BADREQ=HiddenStatusCode(400,'Bad Request')
	C401=UNAUTHORIZED=HiddenStatusCode(401,'Unauthorized')
	C402=PAYMENTREQ=HiddenStatusCode(402,'Payment Required')
	C403=FORBIDDEN=HiddenStatusCode(403,'Forbidden')
	C404=NOTFOUND=HiddenStatusCode(404,'Not Found')
	C405=METHODNALLOWED=HiddenStatusCode(405,'Method Not Allowed')
	C406=NACCEPTABLE=HiddenStatusCode(406,'Not Acceptable')
	C407=PROXYAUTHREQ=HiddenStatusCode(407,'Proxy Authentication Required')
	C408=REQTIMEOUT=HiddenStatusCode(408,'Request Time-out')
	C409=CONFLICT=HiddenStatusCode(409,'Conflict')
	C410=GONE=HiddenStatusCode(410,'Gone')
	C411=LENGTHREQ=HiddenStatusCode(411,'Length Required')
	C412=PRECONDFAILED=HiddenStatusCode(412,'Precondition Failed')
	C413=REQENTTOOBIG=HiddenStatusCode(413,'Request Entity Too Large')
	C414=REQURITOOBIG=HiddenStatusCode(414,'Request-URI Too Large')
	C415=UNSUPMEDIATYPE=HiddenStatusCode(415,'Unsupported Media Type')
	C416=REQRANGENOTSATS=HiddenStatusCode(416,'Requested range not satisfiable')
	C417=EXPECTATIONFAILED=HiddenStatusCode(417,'Expectation Failed')
	C500=INTERNALSERVERERR=HiddenStatusCode(500,'Internal Server Error')
	C501=NOTIMPLEMENTED=HiddenStatusCode(501,'Not Implemented')
	C502=BADGATEWAY=HiddenStatusCode(502,'Bad Gateway')
	C503=SERVICEUNAVAIL=HiddenStatusCode(503,'Service Unavailable')
	C504=GATEWAYTIMEOUT=HiddenStatusCode(504,'Gateway Time-out')
	C505=HTTPVERNSUPP=HiddenStatusCode(505,'HTTP Version not supported')

class HiddenHTTPType(object):
	def __init__(self, code, name):
		self.code=code
		self.name=name

class HTTPType(object):
	Response=HiddenHTTPType(64313,'Response')
	GET=HiddenHTTPType(91603,'GET')
	POST=HiddenHTTPType(514320,'POST')

class URL(object):
	def __init__(self, rawurl):
		self.raw=rawurl
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

		if self.path:
			self.path=self.path.strip()
			if self.path[0]=='/':
				self.path=self.path[1:]

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
							self.type=None # TODO erro
						self.url=URL(url)
						self.version=float(version.split('/')[1])
						httpHeader=True

				elif not blankSpace:
					if (line.strip()=="" or not line) and self.type==HTTPType.POST:
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
			if self.data:
				self.data=self.data.strip()
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


	def toString(self):
		if self.type==HTTPType.Response:
			if self.status:
				message="HTTP/"+str(self.version)+' '+str(self.status.code)+' '+self.status.name+'\n'
				if self.server:
					message+="Server: "+self.server+'\n'
				if self.contenttype:
					message+="Content-Type: "+self.contenttype+'\n'
				now=datetime.now()
				message+="Date: "+"%s, %02d %s %04d %02d:%02d:%02d GMT\n"%(["Mon","Tue","Wed","Thu","Fri","Sat","Sun"][now.weekday()],now.day,["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][now.month-1],now.year,now.hour,now.minute,now.second)
				if self.data:
					message+='Content-Length: '+str(len(self.data))+'\n'
					message+='\n'+self.data+'\n'
				return message
			return "HTTP/1.0 500 Internal Server Error\n"
		else:
			if self.version:
				message=self.type.name+' '+self.url.raw+' '+"HTTP/"+str(self.version)+'\n'
				if self.useragent:
					message+="User-Agent: "+self.useragent+'\n'
				if self.contenttype:
					message+="Content-Type: "+self.contenttype+'\n'
				if self.host:
					message+="Host: "+self.host+'\n'
				if self.accept:
					message+="Accept: "+self.accept+'\n'
				if self.acceptlanguage:
					message+="Accept-Language: "+self.acceptlanguage+'\n'
				if self.acceptencoding:
					message+="Accept-Enconding: "+self.acceptencoding+'\n'
				if self.connection:
					message+="Connection: "+self.connection+'\n'
				if self.contentlength:
					message+="Content-Length: "+self.contentlength+'\n'
				if self.data:
					message+='\n'+self.data+'\n'
				return message
			return "HTTP/1.0 500 Internal Server Error\n"

	def debug(self):
		if self.type:
			sys.stdout.write('type: ')
			sys.stdout.write('\tcode: ')
			print (self.type.code)
			sys.stdout.write('\tname: ')
			print (self.type.name)
		else:
			print ('type: None')
		if self.url:
			sys.stdout.write('url: ')
			sys.stdout.write('\trawurl: ')
			print (self.url.raw)
			sys.stdout.write('\tprotocol: ')
			print (self.url.protocol)
			sys.stdout.write('\tdomain: ')
			print (self.url.domain)
			sys.stdout.write('\tport: ')
			print (self.url.port)
			sys.stdout.write('\tpath: ')
			print (self.url.path)
			sys.stdout.write('\tresource: ')
			print (self.url.resource)
			sys.stdout.write('\tquery: ')
			print (self.url.query)
			sys.stdout.write('\tfragment: ')
			print (self.url.fragment)
		else:
			print ('url: None')
		sys.stdout.write('version: ')
		print (self.version)
		sys.stdout.write('data: ')
		print (self.data)
		sys.stdout.write('useragent: ')
		print (self.useragent)
		sys.stdout.write('contenttype: ')
		print (self.contenttype)
		sys.stdout.write('contentlength: ')
		print (self.contentlength)
		sys.stdout.write('host: ')
		print (self.host)
		sys.stdout.write('accept: ')
		print (self.accept)
		sys.stdout.write('acceptlanguage: ')
		print (self.acceptlanguage)
		sys.stdout.write('acceptencoding: ')
		print (self.acceptencoding)
		sys.stdout.write('connection: ')
		print (self.connection)
		sys.stdout.write('status: ')
		print (self.status)
		sys.stdout.write('server: ')
		print (self.server)

	@staticmethod
	def toJson(http):
		return json.dumps(http.__dict__)

	@staticmethod
	def fromJson(jsonstr):
		return json.loads(jsonstr, object_hook=lambda d: HTTP(**d))