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
			print("coucou")
			client, addr = self.__s.accept()
			print("coucou2")
			#if not (client.gethostname() in self.__database):
			self._register(client)
			print("coucou3")
			client.close()
			#recevoir des requetes
			#file d'attente
			
	def _register(self, client):
		try:
			print("coucou2.5")
			clientData = self._receive(client).decode()
			print(clientData)
			clientData = clientData[1:len(clientData)-1]
			print(clientData)
			clientData = clientData.split(', ')
			print(clientData)
			self.__database[clientData[0]] = (clientData[1], clientData[2])
			print(clientData[0]+" s'est connecte au serveur")
		except OSError:
			print("Erreur lors de la reception des donnees client")
			
	def _receive(self, client):
		chunks = []
		finished = False
		while not finished:
			data = client.recv(1024)
			print(data)
			chunks.append(data)
			finished = data == b''
			print(finished)
		return b''.join(chunks)
			
class ChatClient():
	def __init__(self, host=socket.gethostname(), port=5001):
		s = socket.socket()
		#s = socket.socket(type=socket.SOCK_DGRAM)
		s.settimeout(25)
		s.bind((host,port))
		self.__s = s
		print('Utilisateur {} : Port {}'.format(host, port))
		addrinfoListOfTuples = socket.getaddrinfo(host, port)
		ipAddress=''
		for addrinfoTuple in addrinfoListOfTuples:
			if addrinfoTuple[0] is socket.AF_INET:
				ipAddress = addrinfoTuple[4][0]
				break
		print(socket.gethostname())
		self.__name=socket.gethostname()
		self.__ipAddress=ipAddress
		self.__port=port
		print(self.getInfo)
		print(socket.gethostname())
		print(ipAddress)
		
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
		threading.Thread(target=self._receive).start()
		while self.__running:
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
		self._join(param)
		self._send(str(self.getInfo))
		
	def _exit(self):
		self.__running = False
		self.__address = None
		self.__s.close()
	
	def _quit(self):
		self.__address = None
		
	def _join(self, param):
		tokens = param.split(' ')
		if len(tokens) == 2:
			try:
				self.__address = (socket.gethostbyname(tokens[0]), int(tokens[1]))
				self.__s.connect(self.__address)
				print('Connecte a {}:{}'.format(*self.__address))
			except OSError:
				print("Erreur lors de la connexion")
				
	def _send(self, param):
		print("send")
		if self.__address is not None:
			#try:
			print(self.__address)
			message = param.encode()
			totalsent = 0
			while totalsent < len(message):
				sent = self.__s.send(message[totalsent:])
				#sent = self.__s.sendto(message[totalsent:], self.__address)
				totalsent += sent
			print("sent")
			self.__s.shutdown(socket.SHUT_RDWR)
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
	if len(sys.argv) == 4 and sys.argv[1] == 'client':
		ChatClient(sys.argv[2], int(sys.argv[3])).run()
	elif len(sys.argv) == 2 and sys.argv[1]  == 'server':
		EchoServerPlus().run()
	else:
		EchoServerPlus().run()
		#ChatClient(socket.gethostname(), 5001).run()