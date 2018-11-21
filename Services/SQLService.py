#!/usr/bin/env python
# -*- coding: utf-8 -*-
import psycopg2
import time
import json


class SQLHandler(object):
	def __init__(self):
		self.host 		= "127.0.0.1"
		self.port		= "5432"
		self.dbname 	= "nyxdb"
		self.user 		= "postgres"
		self.password	= "postgres"

	def connect(self):
		conn_string = "host='"+self.host+"' port='"+self.port+"' dbname='"+self.dbname+"' user='"+self.user+"' password='"+self.password+"'"
		self.conn = psycopg2.connect(conn_string)
		self.conn.set_client_encoding('UTF8')
		self.conn.autocommit = True
		self.query = self.conn.cursor()
		self.query.execute("set application_name = 'NYX - Back-end';")
		self.conn.commit()

	############

	def createAccount(self,email,hash,salt,firstname,lastname,accesslevel,cpf,token):                                                                                            
		self.query.execute("INSERT INTO accounts(\"email\",\"hash\",\"salt\",\"firstname\",\"lastname\",\"accesslevel\",\"cpf\",\"active\",\"timeregistered\") VALUES ('"+email+"','"+hash+"','"+salt+"','"+firstname+"','"+lastname+"',"+str(accesslevel)+","+str(cpf)+",'"+token+"',"+str(long(round(time.time()*1000)))+");")
		self.conn.commit()

	def createNightclub(self,name, cnpj, phone, email, id_address, id_account):                                                                                            
		self.query.execute("INSERT INTO nightclubs(\"name\",\"cnpj\",\"phone\",\"email\",\"id_address\",\"id_account\") VALUES ('"+name+"','"+cnpj+"','"+phone+"','"+email+"',"+str(id_address)+"+,"+str(id_account)+");")
		self.conn.commit()

	def createEvent(self, name, ticketprice, minimumage, startdate, enddate):                                                                                            
		self.query.execute("INSERT INTO events(\"name\",\"ticketprice\",\"minimumage\",\"startdate\",\"enddate\") VALUES ('"+name+"',"+str(ticketprice)+","+str(minimumage)+","+str(startdate)+","+str(enddate)+");")
		self.conn.commit()

	def createAddress(self, zipcode, street, number, xtrainfo, district, city, state, country):                                                                                            
		self.query.execute("INSERT INTO addresses(\"zipcode\",\"street\",\"number\",\"xtrainfo\",\"district\",\"city\",\"state\",\"country\") VALUES ("+str(zipcode)+",'"+street+"',"+str(number)+",'"+xtrainfo+"','"+district+"','"+city+"',"+state+"','"+country+"');")
		self.conn.commit()

	def createMusicGenre(self, name):                                                                                            
		self.query.execute("INSERT INTO musicgenres(\"name\") VALUES ('"+name+"');")
		self.conn.commit()

	##########

	def getAccount(self,id=None,email=None):
		if (email==None and id!=None):
			self.query.execute("SELECT id, email, firstname, lastname, accesslevel, cpf, active, timeregistered FROM accounts WHERE id="+str(id)+";")
		elif (email!=None and id==None):
			self.query.execute("SELECT id, email, firstname, lastname, accesslevel, cpf, active, timeregistered FROM accounts WHERE email='"+email+"';")
		else:
			return None #TODO ERROR
		result=self.query.fetchone()
		if result == None:
			return None
		else:
			return Account(result[0],result[1],result[2],result[3],result[4],result[5],result[6],result[7])	

	def getAccountSecurityInfo(self,email):
		self.query.execute("SELECT hash, salt, logintoken, id FROM accounts WHERE email='"+email+"';")
		result=self.query.fetchone()
		if result == None:
			return None
		else:
			return {"hash":result[0], "salt":result[1],"logintoken":result[2] ,"id":result[3]}

	def getNightclubs(self):
		self.query.execute("SELECT id, name, cnpj, phone, email, address FROM nightclubs;")
		result = list(self.query)
		nightclubs=[]
		for nightclub in result:
			nightclubs.append(Nightclub(nightclub[0],nightclub[1],nightclub[2],nightclub[3],nightclub[4],nightclub[5]))
		return Nightclub.listToJson(nightclubs)

	def getNightclubs(self, id_account):
		self.query.execute("SELECT id, name, cnpj, phone, email, address FROM nightclubs WHERE id_account="+str(id_account)+";")
		result = list(self.query)
		nightclubs=[]
		for nightclub in result:
			nightclubs.append(Nightclub(nightclub[0],nightclub[1],nightclub[2],nightclub[3],nightclub[4],nightclub[5]))
		return Nightclub.listToJson(nightclubs)

	def getEvents(self):
		self.query.execute("SELECT id, name, ticketprice, minimumage, startdate, enddate FROM events;")
		result = list(self.query)
		events=[]
		for event in result:
			self.query.execute("SELECT M.id,M.name FROM musicgenres INNER JOIN eventmusicgenres EM ON M.id=EM.id_genre WHERE EM.id_event="+event[0]+";")
			result2 = list(self.query)
			genres=[]
			for genre in result2:
				genres.append(Musicgenre(genre[0],genre[1]))
			events.append(Event(event[0],event[1],event[2],event[3],event[4],event[5],genres))
		return Event.listToJson(events)

	def getEvents(self,id_nightclub):
		self.query.execute("SELECT E.id, E.name, E.ticketprice, E.minimumage, E.startdate, E.enddate FROM events E INNER JOIN nightclubevents NE ON E.id=NE.id_event WHERE NE.id_nightclub="+str(id_nightclub)+";")
		result = list(self.query)
		events=[]
		for event in result:
			self.query.execute("SELECT M.id,M.name FROM musicgenres INNER JOIN eventmusicgenres EM ON M.id=EM.id_genre WHERE EM.id_event="+event[0]+";")
			result2 = list(self.query)
			genres=[]
			for genre in result2:
				genres.append(Musicgenre(genre[0],genre[1]))
			events.append(Event(event[0],event[1],event[2],event[3],event[4],event[5],genres))
		return Event.listToJson(events)

	def getMusicgenres(self):
		self.query.execute("SELECT id,name FROM musicgenres;")
		result = list(self.query)
		genres=[]
		for genre in result:
			genres.append(Musicgenre(genre[0],genre[1]))
		return Musicgenre.listToJson(genres)

	def getMusicgenres(self,id_events):
		self.query.execute("SELECT M.id,M.name FROM musicgenres INNER JOIN eventmusicgenres EM ON M.id=EM.id_genre WHERE EM.id_event="+str(id_events)+";")
		result = list(self.query)
		genres=[]
		for genre in result:
			genres.append(Musicgenre(genre[0],genre[1]))
		return Musicgenre.listToJson(genres)

	##########

	def checkIfAccountExists(self,id=None,email=None):
		if (email==None and id!=None):
			self.query.execute("SELECT COUNT(*) FROM accounts WHERE id="+str(id)+";")
			return self.query.fetchone()[0]!=0
		elif (email!=None and id==None):
			self.query.execute("SELECT COUNT(*) FROM accounts WHERE email='"+email+"';")
			return self.query.fetchone()[0]!=0
		else:
			return True #TODO ERROR

	def updateAccountToken(self,email=None,id=None,token="NOPS"):
		if (email==None and id!=None):
			self.query.execute("UPDATE accounts SET \"active\"='"+token+"' WHERE id="+str(id)+";")
		elif (email!=None and id==None):
			self.query.execute("UPDATE accounts SET \"active\"='"+token+"' WHERE email='"+email+"';")
		self.conn.commit()

	def getRenewPassToken(self,email=None,id=None):
		if (email==None and id!=None):
			self.query.execute("SELECT R.\"token\", R.\"active\", R.\"stamp\" FROM renewpass R INNER JOIN accounts A ON R.\"id_accounts\"=A.\"id\" WHERE A.\"id\"="+id+" AND R.\"active\"=true ORDER BY R.\"stamp\" DESC LIMIT 1;")
		elif (email!=None and id==None):
			self.query.execute("SELECT R.\"token\", R.\"active\", R.\"stamp\" FROM renewpass R INNER JOIN accounts A ON R.\"id_accounts\"=A.\"id\" WHERE A.\"id\"=(SELECT id FROM accounts WHERE email='"+email+"' LIMIT 1) AND R.\"active\"=true ORDER BY R.\"stamp\" DESC LIMIT 1;")
		else:
			return None
		result=self.query.fetchone()
		if result == None:
			return None
		deltatime=time.time()-(float(result[2])/1000)
		if deltatime<0 or deltatime>(24*60*60): # 24 hours validity
			return None
		return result[0]

	def setRenewPassToken(self,requester,token,email=None,id=None):
		if (email==None and id!=None):
			pass
		elif (email!=None and id==None):
			self.query.execute("SELECT id FROM accounts WHERE email='"+email+"' LIMIT 1;")
			id=int(self.query.fetchone()[0])
		else:
			return # ERROR
		self.query.execute("INSERT INTO renewpass(\"id_accounts\",\"requesterip\",\"token\",\"stamp\") VALUES ("+str(id)+",'"+requester+"','"+token+"',"+str(long(round(time.time()*1000)))+");")
		self.conn.commit()

	def disableRenewPassToken(self,modifier,email=None,id=None):
		if (email==None and id!=None):
			pass
		elif (email!=None and id==None):
			self.query.execute("SELECT id FROM accounts WHERE email='"+email+"' LIMIT 1;")
			id=int(self.query.fetchone()[0])
		else:
			return # ERROR
		self.query.execute("SELECT R.\"id\" FROM renewpass R INNER JOIN accounts A ON R.\"id_accounts\"=A.\"id\" WHERE A.\"id\"="+str(id)+" AND R.\"active\"=true ORDER BY R.\"stamp\" DESC LIMIT 1;")
		accid=int(self.query.fetchone()[0])
		self.query.execute("UPDATE renewpass SET \"modifierip\"='"+modifier+"', \"active\"=false WHERE id="+str(accid)+";")

	def updateAccountPassword(self,hash,salt,email=None,id=None):
		if (email==None and id!=None):
			self.query.execute("UPDATE accounts SET \"hash\"='"+hash+"', \"salt\"='"+salt+"' WHERE id="+str(id)+";")
		elif (email!=None and id==None):
			self.query.execute("UPDATE accounts SET \"hash\"='"+hash+"', \"salt\"='"+salt+"' WHERE email='"+email+"';")
		self.conn.commit()

	def removeInactiveAccounts(self,validity):
		removed=0
		self.query.execute("SELECT id,timeregistered FROM accounts WHERE active<>'Active';")
		accs=list(self.query)
		nowts=time.time()
		for acc in accs:
			if nowts-float(acc[1])>=validity:
				self.query.execute("DELETE FROM accounts WHERE id="+str(acc[0])+";")
				self.conn.commit()
				removed=removed+1
		return removed

	def setLoginToken(self,email,logintoken):
		self.query.execute("UPDATE accounts SET \"logintoken\"='"+logintoken+"' WHERE email='"+email+"';")
		self.conn.commit()

	


	
	

	# LINK EVENT TO NIGHT, LINK NIGHT TO ADDRESS, LINK EVENT TO GENRES
	# TODO implementar lists to json nos models