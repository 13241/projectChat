#!/usr/bin/env python3
# appli.py
# author: Damien Abeloos

import socket
import sys
import threading

class EchoServerPlus():
	pass
class EchoClientPLus():
	pass
class AdvancedChat():
	def __init__(self, host=socket.gethostname(), port=3333):
		s = socket.socket(type=socket.SOCK_DGRAM)
		s.settimeout(0.5)
		s.bind((host,port))
		self.__s = s
		print('Utilisateur {} : Port {}'.format(host, port))
		
	def run(self):
		handlers = {
			'/exit': self._exit,
			'/quit': self._quit,
			'/join': self._join,
			'/send': self._send
		}
		self.__running = True
		self.__address = None
		threading.Thread(target=self._receive).start()
		while self.__running:
			line = sys.stdin.readline().rstrip() + ' '
			command = line[:line.index(' ')]
			param = line[line.index(' ')+1:].rstrip()
			if command in handlers:
				try:
					handlers[command]() if param == '' else handlers[command](param)
				except:
					print("Erreur lors de l'execution de la comande.")
			else:
				print('Commande inconnue:', command)
				
	def _exit(self):
		self.__running = False
		self.__address = None
		self.__s.close()
	
	def _quit(self):
		self.__address = None
		
	def _join(self,param):
		tokens = param.split(' ')
		if len(tokens) == 2:
			try:
				self.__address = (socket.gethostbyaddr(tokens[0])[0], int(tokens[1]))
				print('Connecte a {}:{}'.format(*self.__address))
			except OSError:
				print("Erreur lors de l'envoi du message.")
				
	def _send(self, param):
		if self.__address is not None:
			try:
				message = param.encode()
				totalsent = 0
				while totalsent < len(message):
					sent = self.__s.sendto(message[totalsent:], self.__address)
					totalsent += sent
			except OSError:
				print('Erreur lors de la reception du message.')
				
	def _receive(self):
		while self.__running:
			try:
				data, address = self.__s.recvfrom(1024)
				print(data.decode())
			except socket.timeout:
				pass
			except OSError:
				return
				
if __name__ == '__main__':
	if len(sys.argv) == 3:
		AdvancedChat(sys.argv[1], int(sys.argv[2])).run()
	else:
		AdvancedChat().run()