#!/usr/bin/env python
# -*- coding: utf-8 -*-

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email import Charset
from email.generator import Generator

class EmailService(object):

	def __init__(self,email,password,sendmail):
		self.GMAIL_EMAIL="nyxapp@gmail.com"
		self.GMAIL_PASS="type it"

	def configEmail(self,sendNotification,password=None):
		if not self.SENDMAIL:
			BackendServer.log("Ignoring email...")
		else:
			BackendServer.log("Configuring email...")
			if password==None:
			try:
				with open('emailpassword.txt', 'r') as emailpassfile:
					password=emailpassfile.read().replace('\n', '')
			except:
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
