#!/usr/bin/env python
# -*- coding: utf-8 -*-

import select
import time
import SQLHandler
import pbkdf2
import RGenerator
import traceback
import getpass
import sys
import signal
import os
import smtplib
import datetime
import threading
from cStringIO import StringIO



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
		self.CONSTANTHASHSTR="Now I am become Death, the destroyer of worlds."
		self.SENDMAIL=True
		self.mainCrtl=None

	def loop(self):
		try:
			read_sockets,write_sockets,error_sockets = select.select(self.CLIENTS,[],[])
			for sock in read_sockets:
				if sock == self.server_socket: #new connection
					sockfd, addr = self.server_socket.accept()
					sockfd=TSocket(sockfd)
					sockfd.settimeout(self.RECEIVE_TIMEOUT) 
					self.CLIENTS.append(sockfd)
					logger.log("Client ("+sockfd.TSname+") connected!")
					threading.Thread(target=self.listen,args=(sockfd,)).start()
		except Exception as e:
			self.handleException(e)

	def listen(self,sock):
		self.THREADS.append(threading.current_thread())
		while self.running and sock.TSrunning:
			try: #received data
				request=self.recv_timeout(sock,self.RECEIVE_TIMEOUT).strip() # safer than # data = sock.recv(self.RECV_BUFFER)
				requestHandler(request)
			except Exception as e: #client disconnected
				self.handleException(e)
				logger.log("Client ("+sock.TSname+") disconnected!")
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
				try:setupControllers
					result=self.sql.removeInactiveAccounts(self.INACTIVE_ACCOUNT_VALIDITY)
					logger.log(str(result)+" accounts removed!")
				except Exception as e:
					self.handleException(e)
				self.time_removeacc=time.time()


	def shutdown(self):
		logger.log("Shuting down server...")
		self.running=False
		self.THREADS=[]
		for sock in self.CLIENTS:
			if sock != self.server_socket:
				sock.close()
		self.server_socket.close()
		self.CLIENTS = []
		logger.log("Bye <3")
		if self.SENDMAIL:
			try:
				self.SendMail(self.GMAIL_EMAIL,"Servidor encerrado","Server endded\n"+"["+socket.gethostname()+" - "+str(int(round(time.time())))+"]",files=[logger.filename])
			except Exception as e:
				logger.log("Failed to send server end notification email",error=True)
				self.handleException(e)
		sys.exit(0)


	def broadcast_data (self, sock, packet):	
		for socket in CLIENTS:
			if socket != server_socket and socket != sock:
				self.Send(sock,packet)

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
		logger.log("Starting server...")
		self.running=True
		signal.signal(signal.SIGINT, self.interruptSignal)
		self.sql=SQLHandler()
		logger.log("Conntecing to database...")
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
		self.configEmail(True,emailpass)
		self.setupControllers()
		logger.log("Configuring server...")
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
		logger.log(exceptionstr,traceback=True)
		return exceptionstr

	def startThreads(self):
		logger.log("Starting threads...")
		t=threading.Thread(target=self.processEvents)
		self.THREADS.append(t)
		t.start()

	def run(self):
		self.startThreads()
		logger.log("Server started on "+self.SERVER+":"+str(self.PORT)+"!!!")
		while self.running:
			self.loop()
		self.shutdown()

	def Send(self,sock,data):
		packet.crypt()
		data=Packet.ToByteArray(packet)
		sock.send(data)

	def setupControllers(self):
		logger.log("Setting Up controllers...")
		self.mainCrtl=MainController("data/")

	def requestHandler(self,sock,data):
		try:
			request=HTTP(data)
			logger.log("request ["+request.type.name+" - "+request.url.path+request.url.resource+"] received from "+sock.TSname)
			try:
				response=self.mainCrtl.routeRequests()
				self.Send(sock,response.toString())
			except Exception as e:
				errorstr=self.handleException(e)
				error=Error(str(500),{"pointer": errorstr},"Internal Server Error","Error processing request.")
				reponse=HTTP(status=StatusCode.C500,data=Error.listToJson([error]),contenttype="application/json")
				self.Send(sock,response.toString())
		except Exception as e:
			errorstr=self.handleException(e)
			error=Error(str(500),{"pointer": errorstr},"Internal Server Error","Error translating request.")
			reponse=HTTP(status=StatusCode.C500,data=Error.listToJson([error]),contenttype="application/json")
			self.Send(sock,response.toString())


if __name__ == "__main__":
	server = HttpBackendServer()
	server.start()

