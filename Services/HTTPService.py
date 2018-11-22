#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import json
from datetime import datetime

class StatusCode(object):
	def __init__(self, code, name):
		self.code=code
		self.name=name

	C100=CONTINUE=StatusCode(100,'Continue')
	C101=SWITCHING=StatusCode(101,'Switching Protocols')
	C200=OK=StatusCode(200,'OK')
	C201=CREATED=StatusCode(201,'Created')
	C202=ACCEPTED=StatusCode(202,'Accepted')
	C203=NAUTHINFO=StatusCode(203,'Non-Authoritative Information')
	C204=NCONTENT=StatusCode(204,'No Content')
	C205=RCONTENT=StatusCode(205,'Reset Content')
	C206=PCONTENT=StatusCode(206,'Partial Content')
	C300=MULTICHOICES=StatusCode(300,'Multiple Choices')
	C301=MOVED4EVER=StatusCode(301,'Moved Permanently')
	C302=FOUND=StatusCode(302,'Found')
	C303=SEEOTHER=StatusCode(303,'See Other')
	C304=NMODIFIED=StatusCode(304,'Not Modified')
	C305=USEPROXY=StatusCode(305,'Use Proxy')
	C307=TMPREDIRECTED=StatusCode(307,'Temporary Redirect')
	C400=BADREQ=StatusCode(400,'Bad Request')
	C401=UNAUTHORIZED=StatusCode(401,'Unauthorized')
	C402=PAYMENTREQ=StatusCode(402,'Payment Required')
	C403=FORBIDDEN=StatusCode(403,'Forbidden')
	C404=NOTFOUND=StatusCode(404,'Not Found')
	C405=METHODNALLOWED=StatusCode(405,'Method Not Allowed')
	C406=NACCEPTABLE=StatusCode(406,'Not Acceptable')
	C407=PROXYAUTHREQ=StatusCode(407,'Proxy Authentication Required')
	C408=REQTIMEOUT=StatusCode(408,'Request Time-out')
	C409=CONFLICT=StatusCode(409,'Conflict')
	C410=GONE=StatusCode(410,'Gone')
	C411=LENGTHREQ=StatusCode(411,'Length Required')
	C412=PRECONDFAILED=StatusCode(412,'Precondition Failed')
	C413=REQENTTOOBIG=StatusCode(413,'Request Entity Too Large')
	C414=REQURITOOBIG=StatusCode(414,'Request-URI Too Large')
	C415=UNSUPMEDIATYPE=StatusCode(415,'Unsupported Media Type')
	C416=REQRANGENOTSATS=StatusCode(416,'Requested range not satisfiable')
	C417=EXPECTATIONFAILED=StatusCode(417,'Expectation Failed')
	C500=INTERNALSERVERERR=StatusCode(500,'Internal Server Error')
	C501=NOTIMPLEMENTED=StatusCode(501,'Not Implemented')
	C502=BADGATEWAY=StatusCode(502,'Bad Gateway')
	C503=SERVICEUNAVAIL=StatusCode(503,'Service Unavailable')
	C504=GATEWAYTIMEOUT=StatusCode(504,'Gateway Time-out')
	C505=HTTPVERNSUPP=StatusCode(505,'HTTP Version not supported')

class HTTPType(object):
	def __init__(self, code, name):
		self.code=code
		self.name=name

	Response=HTTPType(64313,'Response')
	GET=HTTPType(91603,'GET')
	POST=HTTPType(514320,'POST')

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