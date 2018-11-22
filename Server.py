#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket
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
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email import Charset
from email.generator import Generator


class TSocket(object):
	def __init__(self, sock):
		self.sock=sock
		#extra attributes
		sockdata=sock.getpeername()
		self.TSname=sockdata[0]+":"+str(sockdata[1])
		self.TSrunning=True

	def __getattr__(self, attr):
		if hasattr(self.sock, attr):
			def wrapper(*args, **kwargs):
				return getattr(self.sock, attr)(*args, **kwargs)
			return wrapper
		raise AttributeError(attr)

	def close(self):
		try:
			super(TSocket, self).close()
		except:
			pass
		self.TSrunning=False

class BackendServer(object):
	LOGFILENAME="logs/backend_"+str(int(time.time()))+".log"
	def __init__(self):
		self.running=False
		self.CLIENTS = []    			# list of socket clients
		self.RECV_BUFFER = 32768 		# Advisable to keep it as an exponent of 2
		self.THREADS = []
		self.SERVER = "127.0.0.1" 		
		# self.SERVER = "31.220.54.249" 		
		self.PORT = 5000
		self.GMAIL_EMAIL = "nyxapp@gmail.com"
		self.GMAIL_PASS = "type it"
		self.CONNECTION_TIMEOUT=60 #60s to avoid unnecessary processing
		self.INACTIVE_ACCOUNT_VALIDITY=48*60*60
		self.RECEIVE_TIMEOUT=0.2
		self.time_timeout=time.time()
		self.time_removeacc=time.time()
		self.CONSTANTHASHSTR="Now I am become Death, the destroyer of worlds."
		self.SENDMAIL=True

	def loop(self):
		try:
			read_sockets,write_sockets,error_sockets = select.select(self.CLIENTS,[],[])
			for sock in read_sockets:
				if sock == self.server_socket: #new connection
					sockfd, addr = self.server_socket.accept()
					sockfd=TSocket(sockfd)
					sockfd.settimeout(self.RECEIVE_TIMEOUT) 
					self.CLIENTS.append(sockfd)
					BackendServer.log("Client ("+sockfd.TSname+") connected!")
					threading.Thread(target=self.listen,args=(sockfd,)).start()
		except Exception as e:
			self.handleException(e)

	def listen(self,sock):
		self.THREADS.append(threading.current_thread())
		while self.running and sock.TSrunning:
			try: #received data
				data = self.recv_timeout(sock,self.RECEIVE_TIMEOUT) # safer than # data = sock.recv(self.RECV_BUFFER)
				reading=True
				while reading and len(data)>2:
					reading=False
					length=data[1]+''+data[0]
					length=int(length.encode('hex'), 16)
					if(length<len(data)):
						packetdata=data[2:]
						if(len(packetdata)<length):
							raise Exception('Packet with wrong size ('+str(len(packetdata))+'), expected: '+str(length))
						if(len(packetdata)>length):
							BackendServer.log("Warning:: Client ("+sock.TSname+") sended nested packet("+str(len(packetdata))+'), expected: '+str(length)+"!")
							packetdata=data[2:(2+length)]
							data=data[(2+length):]
							reading=True
						if(len(packetdata)==length):
							pcktreceived=Packet.FromByteArray(packetdata)
							pcktreceived.decrypt()
							self.packetHandler(sock,pcktreceived)
						else:
							raise Exception('Packet with wrong size ('+str(len(packetdata))+'), expected: '+str(length))
			except Exception as e: #client disconnected
				self.handleException(e)
				BackendServer.log("Client ("+sock.TSname+") disconnected!")
				sock.close()
				self.CLIENTS.remove(sock)
		try:
			self.THREADS.remove(threading.current_thread())
		except:
			pass

	def processEvents(self):
		while self.running:
			current_time=time.time()
			delta_timeout=current_time-self.time_timeout
			delta_removeacc=current_time-self.time_removeacc
			if delta_timeout>=self.CONNECTION_TIMEOUT:
				self.checkAllConnections()
				self.time_timeout=time.time()

			if delta_removeacc>=self.INACTIVE_ACCOUNT_VALIDITY:
				try:
					result=self.sql.removeInactiveAccounts(self.INACTIVE_ACCOUNT_VALIDITY)
					BackendServer.log(str(result)+" accounts removed!")
				except Exception as e:
					self.handleException(e)
				self.time_removeacc=time.time()


	def shutdown(self):
		BackendServer.log("Shuting down server...")
		self.running=False
		self.THREADS=[]
		for sock in self.CLIENTS:
			if sock != self.server_socket:
				sock.close()
		self.server_socket.close()
		self.CLIENTS = []
		BackendServer.log("Bye <3")
		if self.SENDMAIL:
			try:
				self.SendMail(self.GMAIL_EMAIL,"Servidor encerrado","Server endded\n"+"["+socket.gethostname()+" - "+str(int(round(time.time())))+"]",files=[BackendServer.LOGFILENAME])
			except Exception as e:
				BackendServer.log("Failed to send server end notification email",error=True)
				self.handleException(e)
		sys.exit(0)

	def checkAllConnections(self):
		for sock in self.CLIENTS:
			if sock != self.server_socket:
				self.checkConnection(sock)

	def checkConnection(self, sock):
		try:
			self.Send(sock,Packet(Packet.CONTROL,"Are you there?"))
		except:
			BackendServer.log("Client ("+sock.TSname+") disconnected due inactivity!")
			sock.close()
			self.CLIENTS.remove(sock)

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

	@staticmethod
	def log(message,error=False,traceback=False,printonscreen=True):
		now = datetime.datetime.now()
		nowstr=now.strftime("%Y%m%d-%H:%M:%S.")+'{:06d}'.format(now.microsecond)
		info_header="["+socket.gethostname()+"|"+nowstr+"] "
		fail_delimiter="***********************************************"
		error_header  ="*--------------------ERROR--------------------*"
		traceb_header ="*------------------TRACE_BACK------------------"
		formatted_message =""
		if error or traceback:
			formatted_message=info_header+'\n'+fail_delimiter+'\n'
			if error:
				formatted_message+=error_header+'\n'
			if traceback:
				formatted_message+=traceb_header+'\n'
			formatted_message+=fail_delimiter+'\n'
			formatted_message+=message+'\n'
			formatted_message+=fail_delimiter
		else:
			formatted_message=info_header+message
		if printonscreen:
			print (formatted_message)
		formatted_message+='\n'
		with open(BackendServer.LOGFILENAME, "a") as logfile:
			logfile.write(formatted_message)

	def interruptSignal(self,signal, frame):
		self.shutdown()

	def start(self):
		BackendServer.log("Starting server...")
		self.running=True
		signal.signal(signal.SIGINT, self.interruptSignal)
		self.sql=SQLHandler()
		BackendServer.log("Conntecing to database...")
		self.sql.connect()
		self.config()
		self.run()

	def configEmail(self,sendNotification,password=None):
		if not self.SENDMAIL:
			BackendServer.log("Ignoring email...")
		else:
			BackendServer.log("Configuring email...")
			if password==None:
				passasker="Digite a senha do email "+self.GMAIL_EMAIL+":"
				print (passasker) #no need to print on log
				self.GMAIL_PASS=getpass.getpass()
			else:
				self.GMAIL_PASS=password
			if sendNotification:
				try:
					self.SendMail(self.GMAIL_EMAIL,"Servidor iniciado","Server started\n"+"["+socket.gethostname()+" - "+str(int(round(time.time())))+"]")
				except Exception as e:
					BackendServer.log("Failed to send server start notification email",error=True)
					self.SENDMAIL=False
					self.handleException(e)


	def config(self):
		emailpass=None
		try:
			with open('emailpassword.txt', 'r') as emailpassfile:
				emailpass=emailpassfile.read().replace('\n', '')
		except:
			pass
		self.configEmail(True,emailpass)
		BackendServer.log("Configuring server...")
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
		BackendServer.log(exceptionstr,traceback=True)

	def startThreads(self):
		BackendServer.log("Starting threads...")
		t=threading.Thread(target=self.processEvents)
		self.THREADS.append(t)
		t.start()

	def run(self):
		self.startThreads()
		BackendServer.log("Server started on "+self.SERVER+":"+str(self.PORT)+"!!!")
		while self.running:
			self.loop()
		self.shutdown()

	def Send(self,sock,packet,recall=True):
		packet.crypt()
		data=Packet.ToByteArray(packet)
		maxsize=1480
		if recall:
			hugepacketid=str("%.6f" % time.time())
		if len(data) > (maxsize) and recall:
			data=data[2:]
			spldata=[data[i:i+maxsize] for i in range(0, len(data), maxsize)]
			for i in range(len(spldata)):
				self.Send(sock,Packet(Packet.HUGEPACKET,hugepacketid+Packet.SEPARATOR+str(i)+Packet.SEPARATOR+str(len(spldata))+Packet.SEPARATOR+spldata[i]),recall=False)
		else:
			sock.send(data)

	def SendMail(self,destination,subject,text,destination_name=None,html='',files=None,sender=None): # check https://www.google.com/settings/security/lesssecureapps
		if self.SENDMAIL:
			server_ssl = smtplib.SMTP_SSL("smtp.gmail.com", 465)
			server_ssl.ehlo() # optional, called by login()
			server_ssl.login(self.GMAIL_EMAIL, self.GMAIL_PASS)  # ssl server doesn't support or need tls, so don't call server_ssl.starttls() 
			if sender==None:
				sender=self.GMAIL_EMAIL
				sender_name=u'NYX Dev Team'
			else:
				sender_name=sender
			if(destination_name==None):
				destination_name=destination.split('@')[0]
			from_address = [sender_name, sender]
			recipient = [destination_name, destination]
			Charset.add_charset('utf-8', Charset.QP, Charset.QP, 'utf-8')
			msg = MIMEMultipart('alternative')# 'alternative’ MIME type – HTML and plain text bundled in one e-mail message
			msg['Subject'] = "%s" % Header(subject, 'utf-8')
			msg['From'] = "\"%s\" <%s>" % (Header(from_address[0], 'utf-8'), from_address[1])
			msg['To'] = "\"%s\" <%s>" % (Header(recipient[0], 'utf-8'), recipient[1])
			if html=='':
				html=text
			htmlpart = MIMEText(html, 'html', 'UTF-8')
			textpart = MIMEText(text, 'plain', 'UTF-8')
			msg.attach(htmlpart)
			msg.attach(textpart)
			for f in files or []:
				try:
					with open(f, "rb") as file:
						part = MIMEApplication(file.read(),Name=basename(f))
					part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
					msg.attach(part)
				except Exception as e:
					self.handleException(e)
			str_io = StringIO()
			g = Generator(str_io, False)
			g.flatten(msg)
			server_ssl.sendmail(self.GMAIL_EMAIL, destination, str_io.getvalue())
			server_ssl.close()#server_ssl.quit()
			BackendServer.log("Email sent to '"+destination+"' about '"+subject+"'")

	def SendConfirmationMail(self,destination,token):
		self.SendMail(destination,"[NYX] Ative sua conta!","Seu código é: "+token)

	def SendRenewMail(self,destination,token):
		self.SendMail(destination,"[NYX] Altere sua senha!","Seu código é: "+token+"\n Valido por 24 horas")

	def SendFeedbackMail(self,sender,type,message):
		self.SendMail(self.GMAIL_EMAIL,"[Feedback] Tipo: "+type+"!","Mensagem do usuario:\n"+message,sender=sender)


	def packetHandler(self,sock,packet):
		BackendServer.log("Packet ["+Packet.getPacketName(packet)+"] received from "+sock.TSname)
		data=packet.data
		if packet.type==Packet.CONTROL:
			try:
				pass
			except Exception as e:
				self.handleException(e)

		elif packet.type==Packet.LOGIN:
			try:
				email,password=data.split(Packet.SEPARATOR)
				email=email.strip()
				password=password.strip()
				securityInfo=self.sql.getUserSecurityInfo(email)
				if securityInfo == None:
					self.Send(sock,Packet(packet.type,"Fail"+Packet.SEPARATOR+"Usuário não cadastrado!"))
				else:
					hash=pbkdf2.PBKDF2(password,securityInfo["salt"],666).hexread(32)
					if hash==securityInfo["hash"]:
						user=self.sql.getUser(id=securityInfo["id"])
						self.Send(sock,Packet(packet.type,"Sucess"+Packet.SEPARATOR+User.toJson(user)))
					else:
						self.Send(sock,Packet(packet.type,"Fail"+Packet.SEPARATOR+"Usuário ou senha incorretos!"))
			except Exception as e:
				self.handleException(e)
				self.Send(sock,Packet(packet.type,"Fail"+Packet.SEPARATOR+"Problema de processamento, tente mais tarde!"))
		elif packet.type==Packet.SIGNIN:
			try:
				email,password,firstname,lastname,school,state,city=data.split(Packet.SEPARATOR)
				email=email.strip()
				password=password.strip()
				firstname=firstname.strip()
				lastname=lastname.strip()
				school=school.strip()
				state=state.strip()
				city=city.strip()
				if not self.sql.checkIfUserExists(email=email):
					salt=RGenerator.genSalt()
					hash=pbkdf2.PBKDF2(password,salt,666).hexread(32)
					token=RGenerator.genToken()
					self.sql.createUser(email,hash,salt,firstname,lastname,school,state,city,token)
					self.Send(sock,Packet(packet.type,"Sucess"))
					self.SendConfirmationMail(email,token)
				else:
					self.Send(sock,Packet(packet.type,"Fail"+Packet.SEPARATOR+"Usuário já cadastrado"))
			except Exception as e:
				self.handleException(e)
				self.Send(sock,Packet(packet.type,"Fail"+Packet.SEPARATOR+"Problema de processamento, tente mais tarde!"))
		elif packet.type==Packet.LOGOUT:
			try:
				sock.close()
				self.CLIENTS.remove(sock)
			except Exception as e:
				self.handleException(e)
			finally:
				self.Send(sock,Packet(packet.type,"Sucess"))

		elif packet.type==Packet.RESENDTOKEN:
			try:
				email=data.split(Packet.SEPARATOR)
				email=email.strip()
				token=RGenerator.genToken()
				self.sql.updateUserToken(email=email,tpken=token)
				self.SendConfirmationMail(email,token)
				self.Send(sock,Packet(packet.type,"Sucess"))
			except Exception as e:
				self.handleException(e)
				self.Send(sock,Packet(packet.type,"Fail"+Packet.SEPARATOR+"Problema de processamento, tente mais tarde!"))
		elif packet.type==Packet.CHECKTOKEN:
			try:
				email,token=data.split(Packet.SEPARATOR)
				email=email.strip()
				token=token.strip()
				user=self.sql.getUser(email=email)
				if user.active==token:
					self.sql.updateUserToken(email=email,token="Active")
					self.Send(sock,Packet(packet.type,"Sucess"))
				else:
					self.Send(sock,Packet(packet.type,"Fail"+Packet.SEPARATOR+"Token incorreto!"))
			except Exception as e:
				self.handleException(e)
				self.Send(sock,Packet(packet.type,"Fail"+Packet.SEPARATOR+"Problema de processamento, tente mais tarde!"))
		elif packet.type==Packet.TOKENPWD:
			try:
				email=data.split(Packet.SEPARATOR)[0]
				email=email.strip()
				if self.sql.checkIfUserExists(email=email):
					token=self.sql.getRenewPassToken(email=email)
					if token==None:
						token=RGenerator.genToken(10);
						requester=sock.TSname
						self.sql.setRenewPassToken(requester,token,email=email)
						self.SendRenewMail(email,token)
						self.Send(sock,Packet(packet.type,"Sucess"+Packet.SEPARATOR+"Novo token criado com sucesso!"))
					else:
						self.SendRenewMail(email,token)
						self.Send(sock,Packet(packet.type,"Sucess"+Packet.SEPARATOR+"Já existe um token ativo!"))
				else:
					self.Send(sock,Packet(packet.type,"Fail"+Packet.SEPARATOR+"Email não cadastrado!"))
			except Exception as e:
				self.handleException(e)
				self.Send(sock,Packet(packet.type,"Fail"+Packet.SEPARATOR+"Problema de processamento, tente mais tarde!"))

		elif packet.type==Packet.RENEWPWD:
			try:
				email,token,password=data.split(Packet.SEPARATOR)
				email=email.strip()
				token=token.strip()
				password=password.strip()
				token_sys=self.sql.getRenewPassToken(email=email)
				if token_sys!=None:
					if token_sys==token:
						salt=RGenerator.genSalt()
						hash=pbkdf2.PBKDF2(password,salt,666).hexread(32)
						modifier=sock.TSname
						self.sql.updateUserPassword(hash,salt,email=email)
						self.sql.disableRenewPassToken(modifier,email=email)
						self.Send(sock,Packet(packet.type,"Sucess"+Packet.SEPARATOR+"Senha alterada!"))
					else:
						self.Send(sock,Packet(packet.type,"Fail"+Packet.SEPARATOR+"Token incorreto!"))
				else:
					self.Send(sock,Packet(packet.type,"Fail"+Packet.SEPARATOR+"Token não encontrado ou email incorreto!"))
			except Exception as e:
				self.handleException(e)
				self.Send(sock,Packet(packet.type,"Fail"+Packet.SEPARATOR+"Problema de processamento, tente mais tarde!"))
		elif packet.type==Packet.GETDBINFO:
			try:
				result=data.split(Packet.SEPARATOR)
				dbtype=result[0]
				dbtype=dbtype.strip()
				if dbtype=='schools':
					self.Send(sock,Packet(packet.type,"Sucess"+Packet.SEPARATOR+dbtype+Packet.SEPARATOR+self.sql.getSchools()))
				elif dbtype=='states':
					self.Send(sock,Packet(packet.type,"Sucess"+Packet.SEPARATOR+dbtype+Packet.SEPARATOR+self.sql.getStates()))
				elif dbtype=='cities':
					stateid=result[1]
					stateid=stateid.strip()
					self.Send(sock,Packet(packet.type,"Sucess"+Packet.SEPARATOR+dbtype+Packet.SEPARATOR+self.sql.getCities(stateid)))
			except Exception as e:
				self.handleException(e)
				self.Send(sock,Packet(packet.type,"Fail"+Packet.SEPARATOR+"Problema de processamento, tente mais tarde!"))
		elif packet.type==Packet.SETFACEBOOK:
			try:
				id,fuid=data.split(Packet.SEPARATOR)
				id=id.strip()
				fuid=fuid.strip()
				self.sql.setFacebook(id,fuid)
				self.Send(sock,Packet(packet.type,"Sucess"+Packet.SEPARATOR+fuid))
			except Exception as e:
				self.handleException(e)
				self.Send(sock,Packet(packet.type,"Fail"+Packet.SEPARATOR+"Problema de processamento, tente mais tarde!"))
		elif packet.type==Packet.GETSCORES:
			try:
				type,gameid,param=data.split(Packet.SEPARATOR)
				type=type.strip()
				gameid=gameid.strip()
				param=param.strip()
				result=None
				if type=="facebook_friends":
					param=param.replace("\"","")
					result=self.sql.getFaceFriendsScore(gameid,param)
				elif type=="school":
					result=self.sql.getSchoolScore(gameid,param)
				elif type=="state":
					result=self.sql.getStateScore(gameid,param)
				elif type=="city":
					result=self.sql.getCityScore(gameid,param)
				elif type=="all":
					result=self.sql.getScore(gameid)
				elif type=="player":
					result=self.sql.getPlayerScore(gameid,param)
				if result==None:
					self.Send(sock,Packet(packet.type,"Fail"+Packet.SEPARATOR+"Nenhum resultado encontrado!"))
				else:
					self.Send(sock,Packet(packet.type,"Sucess"+Packet.SEPARATOR+type+Packet.SEPARATOR+result))
			except Exception as e:
				self.handleException(e)
				self.Send(sock,Packet(packet.type,"Fail"+Packet.SEPARATOR+"Problema de processamento, tente mais tarde!"))
		elif packet.type==Packet.SETSCORE:
			try:
				playerid,gameid,score=data.split(Packet.SEPARATOR)
				playerid=playerid.strip()
				gameid=gameid.strip()
				score=score.strip()
				self.sql.setScore(playerid,gameid,score)
				self.Send(sock,Packet(packet.type,"Sucess"))
			except Exception as e:
				self.handleException(e)
				self.Send(sock,Packet(packet.type,"Fail"+Packet.SEPARATOR+"Problema de processamento, tente mais tarde!"))
		elif packet.type==Packet.SETLOGINTOKEN:
			try:
				email,deviceinfo,timestamp=data.split(Packet.SEPARATOR)
				email=email.strip()
				deviceinfo=deviceinfo.strip()
				timestamp=timestamp.strip()
				logintoken=pbkdf2.PBKDF2(email+deviceinfo+timestamp+self.CONSTANTHASHSTR,deviceinfo+timestamp+self.CONSTANTHASHSTR,666).hexread(32)
				self.sql.setLoginToken(email,logintoken)
				self.Send(sock,Packet(packet.type,"Sucess"))
			except Exception as e:
				self.handleException(e)
				self.Send(sock,Packet(packet.type,"Fail"+Packet.SEPARATOR+"Problema de processamento, tente mais tarde!"))
		elif packet.type==Packet.CKLOGINTOKEN:
			try:
				email,deviceinfo,timestamp=data.split(Packet.SEPARATOR)
				email=email.strip()
				deviceinfo=deviceinfo.strip()
				timestamp=timestamp.strip()
				securityInfo=self.sql.getUserSecurityInfo(email)
				if securityInfo != None:
					logintoken=pbkdf2.PBKDF2(email+deviceinfo+timestamp+self.CONSTANTHASHSTR,deviceinfo+timestamp+self.CONSTANTHASHSTR,666).hexread(32)
					if logintoken==securityInfo["logintoken"]:
						user=self.sql.getUser(id=securityInfo["id"])
						self.Send(sock,Packet(Packet.LOGIN,"Sucess"+Packet.SEPARATOR+User.toJson(user)))
					else:
						self.sql.setLoginToken(email,'failedtocheck')
				else:
						self.sql.setLoginToken(email,'scrinfonone')
			except Exception as e:
				self.handleException(e)
				self.Send(sock,Packet(packet.type,"Fail"+Packet.SEPARATOR+"Problema de processamento, tente mais tarde!"))
		elif packet.type==Packet.FEEDBACK:
			try:
				email,type,message=data.split(Packet.SEPARATOR)
				email=email.strip()
				type=type.strip()
				message=message.strip()
				self.SendFeedbackMail(email,type,message)
				self.Send(sock,Packet(packet.type,"Sucess"))
			except Exception as e:
				self.handleException(e)
				self.Send(sock,Packet(packet.type,"Fail"+Packet.SEPARATOR+"Problema de processamento, tente mais tarde!"))


if __name__ == "__main__":
	server = BackendServer()
	server.start()

