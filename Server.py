#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Python imports
import time
import sys
import os
import signal
import socket
import select
import traceback
import threading
from cStringIO import StringIO

# Folder inclusions
sys.path.insert(0, 'Controllers')
sys.path.insert(0, 'DTO')
sys.path.insert(0, 'Services')
sys.path.insert(0, 'Utils')

# Custom imports
from Error import Error
from log import Logger
from MainController import MainController
from AccountController import AccountController
from NightclubController import NightclubController
from EventController import EventController
from EmailService import EmailService
from HTTPService import StatusCode
from HTTPService import HTTP
from SQLService import SQLService
from TSocket import TSocket

# Code
class HttpBackendServer(object):
	def __init__(self,IP="127.0.0.1",port=3000):
		self.logger=Logger("logs/backend_"+str(int(time.time()))+".log")
		self.running=False
		self.THREADS=[]
		self.CLIENTS=[]    			# list of socket clients
		self.RECV_BUFFER=32768 		# Advisable to keep it as an exponent of 2
		self.SERVER=IP	
		self.PORT=port
		self.INACTIVE_ACCOUNT_VALIDITY=48*60*60 # in seconds
		self.RECEIVE_TIMEOUT=0.2
		self.time_removeacc=time.time() # TODO create class for events	

	def loop(self):
		try:
			read_sockets,write_sockets,error_sockets = select.select(self.CLIENTS,[],[])
			for sock in read_sockets:
				if sock == self.server_socket: #new connection
					sockfd, addr = self.server_socket.accept()
					sockfd=TSocket(sockfd)
					sockfd.settimeout(self.RECEIVE_TIMEOUT) 
					self.CLIENTS.append(sockfd)
					self.logger.log("Client ("+sockfd.TSname+") connected!")
					threading.Thread(target=self.listen,args=(sockfd,)).start()
		except Exception as e:
			self.handleException(e)

	def listen(self,sock):
		self.THREADS.append(threading.current_thread())
		while self.running and sock.TSrunning:
			try: #received data
				request=self.recv_timeout(sock,self.RECEIVE_TIMEOUT).strip() # safer than # data = sock.recv(self.RECV_BUFFER)
				self.requestHandler(sock,request)
			except Exception as e: #client disconnected
				self.handleException(e)
				self.logger.log("Client ("+sock.TSname+") disconnected!")
				sock.close()
				self.CLIENTS.remove(sock)
		try:
			self.THREADS.remove(threading.current_thread())
		except:
			pass

	def processEvents(self): # TODO create class for events
		while self.running:
			current_time=time.time()
			delta_removeacc=current_time-self.time_removeacc

			if delta_removeacc>=self.INACTIVE_ACCOUNT_VALIDITY:
				try:
					result=self.sql.removeInactiveAccounts(self.INACTIVE_ACCOUNT_VALIDITY)
					self.logger.log(str(result)+" accounts removed!")
				except Exception as e:
					self.handleException(e)
				self.time_removeacc=time.time()


	def shutdown(self):
		self.logger.log("Shuting down server...")
		self.running=False
		self.THREADS=[]
		for sock in self.CLIENTS:
			if sock != self.server_socket:
				sock.close()
		self.server_socket.close()
		self.CLIENTS = []
		self.logger.log("Bye <3")
		try:
			self.email.SendMail(self.email.GMAIL_EMAIL,"Servidor encerrado","Server endded\n"+"["+socket.gethostname()+" - "+str(int(round(time.time())))+"]",files=[self.logger.filename])
		except Exception as e:
			self.logger.log("Failed to send server end notification email",error=True)
			self.handleException(e)
		sys.exit(0)


	def broadcast_data (self, sock, data):	
		for socket in CLIENTS:
			if socket != server_socket and socket != sock:
				self.Send(sock,data)

	def recv_timeout(self,the_socket,timeout=2):
		if timeout==0:
			return the_socket.recv(self.RECV_BUFFER)
		else:
			the_socket.setblocking(0)#make socket non blocking
			total_data=[];
			data='';
			begin=time.time()
			while True:
				if total_data and time.time()-begin > timeout: #if you got some data, then break after timeout
					break
				elif time.time()-begin > timeout*2: #if you got no data at all, wait a little longer, twice the timeout
					break
				try:
					data = the_socket.recv(self.RECV_BUFFER)
					if data:
						total_data.append(data)
						begin = time.time()
					else:
						time.sleep(0.1)#sleep for sometime to indicate a gap
				except:
					pass
			return ''.join(total_data)

	def interruptSignal(self,signal, frame):
		self.shutdown()

	def start(self):
		self.logger.log("Starting server...")
		self.running=True
		signal.signal(signal.SIGINT, self.interruptSignal)
		self.sql=SQLService()
		self.logger.log("Conntecing to database...")
		self.sql.connect()
		self.config()
		self.run()

	def config(self):
		emailpass=None
		try:
			with open('emailpassword.txt', 'r') as emailpassfile:
				emailpass=emailpassfile.read().replace('\n', '')
		except:
			pass
		self.email=EmailService(self,"nyxapp2018@gmail.com",emailpass)
		self.setupControllers()
		self.logger.log("Configuring server...")
		self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.server_socket.bind((self.SERVER, self.PORT))
		self.server_socket.listen(10)
		self.CLIENTS.append(self.server_socket)

	def handleException(self,e):
		exc_type, exc_value, exc_traceback = sys.exc_info()
		fname = os.path.split(exc_traceback.tb_frame.f_code.co_filename)[1]
		exceptionstr="*** file_name:\n"
		exceptionstr+=fname+'\n'
		exceptionstr+="*** exception:\n"
		exceptionstr+=str(e)+"\n"
		exceptionstr+="*** print_tb:\n"
		str_io = StringIO()
		traceback.print_tb(exc_traceback, limit=1, file=str_io)
		exceptionstr+=str_io.getvalue()
		exceptionstr+="*** print_exception:\n"
		str_io = StringIO()
		traceback.print_exception(exc_type, exc_value, exc_traceback,limit=2, file=str_io)
		exceptionstr+=str_io.getvalue()
		exceptionstr+="*** print_exc:\n"
		str_io = StringIO()
		traceback.print_exc(limit=2, file=str_io)
		exceptionstr+=str_io.getvalue()
		exceptionstr+="*** format_exc, first and last line:\n"
		formatted_lines = traceback.format_exc().splitlines()
		exceptionstr+=formatted_lines[0]+"\n"
		exceptionstr+=formatted_lines[-1]+"\n"
		exceptionstr+="*** format_exception:\n"
		exceptionstr+=repr(traceback.format_exception(exc_type, exc_value,exc_traceback))+'\n'
		exceptionstr+="*** extract_tb:\n"
		exceptionstr+=repr(traceback.extract_tb(exc_traceback))+"\n"
		exceptionstr+="*** format_tb:\n"
		exceptionstr+=repr(traceback.format_tb(exc_traceback))+"\n"
		exceptionstr+="*** tb_lineno:\n"
		exceptionstr+=str(exc_traceback.tb_lineno)
		self.logger.log(exceptionstr,traceback=True)
		return exceptionstr

	def startThreads(self):
		self.logger.log("Starting threads...")
		t=threading.Thread(target=self.processEvents)
		self.THREADS.append(t)
		t.start()

	def run(self):
		self.startThreads()
		self.logger.log("Server started on "+self.SERVER+":"+str(self.PORT)+"!!!")
		while self.running:
			self.loop()
		self.shutdown()

	def Send(self,sock,data):
		sock.send(data)

	def setupControllers(self):
		self.logger.log("Setting Up controllers...")
		self.mainCtrl=MainController(self,"api")
		self.mainCtrl.appendController(AccountController(self,"acc"))
		self.mainCtrl.appendController(NightclubController(self,"nclub"))
		self.mainCtrl.appendController(EventController(self,"nclub/event"))

	def requestHandler(self,sock,data):
		try:
			print (data)
			request=HTTP(data)
			request.client=sock.TSname
			# TODO check host and other info
			request.debug()
			self.logger.log("Request ["+request.type.name+" - "+request.url.path+'/'+request.url.resource+"] received from "+sock.TSname)
			try:
				response=self.mainCtrl.routeRequest(request)
				self.logger.log("Response ["+str(response.status.code)+": "+response.status.name+" - "+request.url.path+'/'+request.url.resource+"] sented to "+sock.TSname)
				self.Send(sock,response.toString())
			except Exception as e:
				errorstr=self.handleException(e)
				error=Error(str(500),{"pointer": errorstr},"Internal Server Error","Error processing request.")
				response=HTTP(status=StatusCode.C500,data=Error.listToJson([error]),contenttype="application/json")
				self.logger.log("Response ["+str(response.status.code)+": "+response.status.name+" - "+request.url.path+'/'+request.url.resource+"] sented to "+sock.TSname)
				responsestr=response.toString()
				self.Send(sock,responsestr)
		except Exception as e:
			errorstr=self.handleException(e)
			error=Error(str(500),{"pointer": errorstr},"Internal Server Error","Error translating request.")
			response=HTTP(status=StatusCode.C500,data=Error.listToJson([error]),contenttype="application/json")
			self.logger.log("Response ["+str(response.status.code)+": "+response.status.name+" - "+request.url.path+'/'+request.url.resource+"] sented to "+sock.TSname)
			responsestr=response.toString()
			self.Send(sock,responsestr)
		try:# TODO check connection type before close-it
			sock.close()
			self.CLIENTS.remove(sock)
		except Exception as e:
			self.handleException(e)


if __name__ == "__main__":
	# server = HttpBackendServer()
	server = HttpBackendServer("192.168.0.14")
	server.start()

