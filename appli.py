#!/usr/bin/env python3
# appli.py
# author: Damien Abeloos

import socket
import sys
import threading

SERVERADDRESS = (socket.gethostname(), 5000)
class EchoServerPlus():
	def __init__(self):
		self.__s = socket.socket()
		self.__s.bind(SERVERADDRESS)
		print('Server on {}:{}'.format(SERVERADDRESS[0], SERVERADDRESS[1]))
		addrinfoListOfTuples = socket.getaddrinfo(SERVERADDRESS[0], SERVERADDRESS[1])
		ipAddress=''
		for addrinfoTuple in addrinfoListOfTuples:
			if addrinfoTuple[0] is socket.AF_INET:
				ipAddress = addrinfoTuple[4][0]
				break
		self.__name='server'
		self.__ipAddress=ipAddress
		self.__port=SERVERADDRESS[1]
		self.__database={}
		print(socket.gethostname())
		print(ipAddress)
		
	def run(self):
		self.__running = True
		self.__s.listen()
		while self.__running:
			client, addr = self.__s.accept()
			#if not (client.gethostname() in self.__database):
			self._register(client)
			print(str(self.__database))
			client.close()
			#recevoir des requetes
			#file d'attente
			
	def _register(self, client):
		try:
			added=False
			clientData = self._receive(client).decode()
			clientData = clientData[1:len(clientData)-1]
			clientData = clientData.split(', ')
			clientData[2]=int(clientData[2])+100
			if clientData[0] in self.__database:
				for i in range(len(self.__database[clientData[0]])):
					if self.__database[clientData[0]][i][1]==clientData[2]: #check port
					#if self.__database[clientData[0]][i][0]==clientData[1]: #check ip
						self.__database[clientData[0]][i] = (clientData[1], clientData[2])
						added = True
				if not added:
					self.__database[clientData[0]].append((clientData[1], clientData[2]))
			else:
				self.__database[clientData[0]] = [(clientData[1], clientData[2])]
			print(clientData[0]+" s'est connecte au serveur")
		except OSError:
			print("Erreur lors de la reception des donnees client")
			
	def _receive(self, client):
		chunks = []
		finished = False
		while not finished:
			data = client.recv(1024)
			print("sent data : "+str(data))
			chunks.append(data)
			finished = data == b''
		return b''.join(chunks)
			
class ChatClient():
	def __init__(self, host=socket.gethostname(), port=5001):
		self.__name=host
		self.__port=port
		self.__maxPortRange= port + 99
		isAServerSocket=True
		self.socketizer(isAServerSocket)
		print('Utilisateur {} : Port {}'.format(host, port))
		print(self.getInfo)
		
	def socketizer(self, isAServerSocket=False):
		try:
			self.__s.close()
		except AttributeError:
			pass
		self.__address = None
		host = self.__name
		port = self.__port
		if isAServerSocket:
			self.__s = socket.socket()
		else:
			self.__s = socket.socket(type=socket.SOCK_DGRAM)
			self.__s.settimeout(4)
		#self.__s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.__s.bind((host,port))
		addrinfoListOfTuples = socket.getaddrinfo(host, port)
		ipAddress=''
		for addrinfoTuple in addrinfoListOfTuples:
			if addrinfoTuple[0] is socket.AF_INET:
				ipAddress = addrinfoTuple[4][0]
				break
		self.__ipAddress=ipAddress
		
	def run(self):
		handlers = {
			'/exit': self._exit,
			'/quit': self._quit,
			'/join': self._join,
			'/send': self._send,
			'/myInfo': self._getInfo,
			'/joinServer': self._joinServer
		}
		self.__running = True
		self.__address = None
		#threading.Thread(target=self._receive).start()
		while self.__running:
			threading.Thread(target=self._receive).start()
			line = sys.stdin.readline().rstrip() + ' '
			command = line[:line.index(' ')]
			param = line[line.index(' ')+1:].rstrip()
			if command in handlers:
				#try:
				handlers[command]() if param == '' else handlers[command](param)
				#except:
				#	print("Erreur lors de l'execution de la comande.")
			else:
				print('Commande inconnue:', command)
	
	def _joinServer(self, param):
		try:
			isAServer = True
			self._join(param, isAServer)
			self._send(str(self.getInfo), isAServer)
			self.__s.shutdown(socket.SHUT_RDWR)
			self.__port += 100
			print(self.getInfo)
			self.socketizer()
		except BrokenPipeError:
			print("Vous etes deja enregistre sur ce serveur")
		
	def _exit(self):
		self.__running = False
		self.__address = None
		self.__s.close()
	
	def _quit(self):
		self.__address = None
		
	def _join(self, param, isAServer=False):
		if not isinstance(isAServer, bool):
			isAServer = False
		self.socketizer(isAServer)
		tokens = param.split(' ')
		if len(tokens) == 2:
			try:
				self.__address = (socket.gethostbyname(tokens[0]), int(tokens[1]))
				if isAServer:
					self.__s.connect(self.__address)
				print('Connecte a {}:{}'.format(*self.__address))
			except OSError as err:
				if err.errno==10048 and self.__port < self.__maxPortRange:
					self.__port+=1
					self._join(param, isAServer)
				else:
					print("Erreur lors de la connexion")
				
	def _send(self, param, isAServer=False):
		if self.__address is not None:
			#try:
			message = param.encode()
			totalsent = 0
			while totalsent < len(message):
				if isAServer:
					sent = self.__s.send(message[totalsent:])
				else:
					sent = self.__s.sendto(message[totalsent:], self.__address)
				totalsent += sent
			#except OSError:
			#	print('Erreur lors de la reception du message.')
				
	def _receive(self):
		while self.__running:
			try:
				data, address = self.__s.recvfrom(1024)
				print(data.decode())
			except socket.timeout:
				pass
			except OSError:
				return
	
	@property
	def getInfo(self):
		return (self.__name, self.__ipAddress, self.__port)
			
	def _getInfo(self):
		print(self.getInfo)
			
if __name__ == '__main__':
	flag = False
	port = 5001
	while not flag:
		try:
			EchoServerPlus().run()
		except OSError:
			try:
				ChatClient(port=port).run()
				flag = True
			except OSError:
				port+=1