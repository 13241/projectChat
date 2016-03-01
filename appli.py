#!/usr/bin/env python3
# appli.py
# author: Damien Abeloos

import socket
import sys
import threading
import traceback


'''
REMARQUE IMPORTANTE : 

le code est configure pour fonctionner sur une machine seule, 
une seule adresse IP, et de nombreux ports. Pour qu'il fonctionne de maniere optimale
sur des machines differentes, il faut modifier EchoServerPlus._register
(commentaires joujou a ajuster)
'''


SERVERADDRESS = (socket.gethostname(), 5000)
class EchoServerPlus():
	'''
	Serveur, lancer une premiere fois l'application pour l'initialiser
	'''
	def __init__(self):
		'''
		constructeur, modifier SERVERADDRESS si besoin de changer le host et le port
		port de connexion par defaut : 5000
		'''
		self.__s = socket.socket()
		self.__s.bind(SERVERADDRESS)
		print('Server on {} : {}'.format(SERVERADDRESS[0], SERVERADDRESS[1]))
		#on recupere l'addresse IP de maniere deterministe :
		addrinfoListOfTuples = socket.getaddrinfo(SERVERADDRESS[0], SERVERADDRESS[1])
		ipAddress=''
		for addrinfoTuple in addrinfoListOfTuples:
			if addrinfoTuple[0] is socket.AF_INET:
				ipAddress = addrinfoTuple[4][0]
				break
		print(ipAddress)
		self.__name=SERVERADDRESS[0]
		self.__ipAddress=ipAddress
		self.__port=SERVERADDRESS[1]
		self.__database={} #contient les informations des clients connectes au serveur
		
	def run(self):
		'''
		routine du serveur, ne s'arrete que lorsqu'on l'eteint
		'''
		self.__running = True
		self.__s.listen(5) #maximum 5 tentatives de connection simultanees en file d'attente
		while self.__running:
			try:
				client, address = self.__s.accept()
				message = self._receive(client).decode()
				#voir readme pour le protocole de communication avec le serveur :
				line = message.rstrip() + ' '
				command = line[:line.index(' ')]
				param = line[line.index(' ')+1:].rstrip()
				if param == '':
					#ajout/retrait de client dans la base de donnees
					self._register(address, command)
					print(str(self.__database))
				else:
					#inputs necessitant une reponse du serveur
					print(message+" from : "+str(address))
					self._answer(client, address, param)
					client.shutdown(socket.SHUT_RDWR)
				client.close()
			except OSError:
				print("Erreur lors de la reception des donnees client")
				traceback.print_exc(file=sys.stdout)
	
	def _register(self, address, info):
		'''
		permet d'ajouter ou de retirer un client de la base de donnees du serveur
		
		pre :	address est un tuple contenant deux donnees : ([str], [int])(ipAddress, port)
				info est un [str] au format : 
				"hostname|_|port" pour une tentative de connection
				"hostname|-|port" pour une tentative de deconnection
		post :	enregistre ou supprime les donnees du client dans la base de donnees si les arguments
				sont valides, affiche un message informatif indiquant ce qui a ete realise
		'''
		try:
			#connexion
			name = info[:info.index('|_|')]
			port = int(info[info.index('|_|')+3:].rstrip())
			clientName = name
			clientIpAddress = address[0]
			clientPort = port
			added = False
			if clientName in self.__database:
				for i in range(len(self.__database[clientName])):
					'''
					interchanger les deux conditions suivantes selon l'utilisation de l'application
					'''
					#condition pour faire joujou tout seul sur son ordi :
					if self.__database[clientName][i][1]==clientPort:#test port (n'accepte pas 2 IP pour le meme port (non ça ne sert a rien))
					#condition pour faire joujou avec plusieurs ordis ou cartes reseau :
					#if self.__database[clientName][i][0]==clientIpAddress:#test ip (n'accepte pas 2 ports pour la meme IP)
						self.__database[clientName][i] = (clientIpAddress, clientPort) #modifie les informations d'un client deja enregistre
						added = True
				if not added:
					self.__database[clientName].append((clientIpAddress, clientPort)) #ajoute des informations pour un nom d'host (plusieurs clients ayant le meme hostname)
			else:
				self.__database[clientName] = [(clientIpAddress, clientPort)] #ajoute un nouveau client et ses informations
			print(clientName+" s'est connecte au serveur")
		except ValueError:
			#deconnexion
			try:
				name = info[:info.index('|-|')]
				port = int(info[info.index('|-|')+3:].rstrip())
				clientName = name
				clientIpAddress = address[0]
				clientPort = port
				added = False
				if clientName in self.__database:
					for i in range(len(self.__database[clientName])):
						if self.__database[clientName][i][1]==clientPort and self.__database[clientName][i][0]==clientIpAddress:
							#suppression des informations client de la base de donnees
							self.__database[clientName].pop(i)
							if self.__database[clientName]==[]:
								#suppression du client
								self.__database.pop(clientName)
				print(clientName+" s'est deconnecte du serveur")
			except:
				print("Arguments non valides")
			
	def _receive(self, client):
		'''
		capture des paquets de donnees envoyes par client
		
		pre :	client est un socket dont la connexion a ete acceptee par le serveur
		post : 	renvoie les donnees envoyees par client (bytes)
		'''
		chunks = []
		finished = False
		while not finished:
			data = client.recv(1024)
			chunks.append(data)
			finished = data == b''
		return b''.join(chunks)
			
	def _answer(self, client, address, request):
		'''
		envoie une reponse a client dependant de request
		
		pre :	client est un socket dont la connexion a ete acceptee par le serveur
				address est un tuple contenant ([str], [int])(ipAddress, port)
				request est un [str] qui peut etre :
				".*" : requete pour obtenir tous les noms d'utilisateur de la base de donnee du serveur
				"hostname" : requete pour obtenir les informations de l'utilisateur hostname
		post :	renvoie un [str] a client contenant la reponse du serveur
		'''
		if request=='.*':
			everyone=[]
			for name in self.__database:
				everyone.append(name)
			answer = '\r\n'.join(everyone)
			answer = "utilisateurs connectes : \r\n" + answer
		elif request in self.__database:
			answer = request + " est connecte via : " + str(self.__database[request])
		else:
			answer = request + " n'est pas connecte"
		try:
			message = answer.encode()
			totalsent = 0
			while totalsent < len(message):
				sent = client.send(message[totalsent:])
				totalsent += sent
		except OSError:
			print('Erreur lors de la reception du message.')
			traceback.print_exc(file=sys.stdout)
		
class ChatClient():
	'''
	client, lancer l'application apres avoir demarre le serveur pour initialiser un client
	'''
	def __init__(self, host=socket.gethostname(), port=5001):
		'''
		constructeur, ports de connexion par defaut : 5001 a 5999
		'''
		self.__name=host
		self.__scPort=port #socket datagram (p2p)
		self.__ssPort=port+100 #socket stream (server)
		self.__maxPortRange= port + 998
		self.__serverAddress = None
		self.__flagMessage=False #evalue si une reception de donnees du serveur est en court ou non
		isAServerSocket=True
		self.socketizer(isAServerSocket) #initialisation du socket stream
		self.socketizer() #initialisation du socket datagram
		print('Utilisateur {} : Port {}'.format(host, port))
		print(self.getInfo)
		
	def socketizer(self, isAServerSocket=False):
		'''
		cree un nouveau socket datagram ou stream en fermant le precedent
		
		pre :	isAServerSocket = True pour un socket stream
				isAServerSocket = False pour un socket datagram
		post :	ferme le socket datagram ou stream, en cree un nouveau
		'''
		try:
			if isAServerSocket:
				self.__ss.close()
			else:
				self.__sc.close()
		except AttributeError:
			#la variable n'etait pas encore initialisee
			pass
		self.__address = None #reset l'addresse de connexion
		host = self.__name
		if isAServerSocket:
			self.__ss = socket.socket()
			port = self.__ssPort
			self.__ss.bind((host,port))
			#self.__ss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)#pas compris l'utilite, ne permet pas de reutiliser un port immediatement apres fermeture
		else:
			self.__sc = socket.socket(type=socket.SOCK_DGRAM)
			port = self.__scPort
			self.__sc.settimeout(4) #4 secondes de delais avant interruption de l'operation
			self.__sc.bind((host,port))
			#self.__sc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		#obtention deterministe de l'addresse IP :
		addrinfoListOfTuples = socket.getaddrinfo(host, port)
		ipAddress=''
		for addrinfoTuple in addrinfoListOfTuples:
			if addrinfoTuple[0] is socket.AF_INET:
				ipAddress = addrinfoTuple[4][0]
				break
		self.__ipAddress=ipAddress
		
	def run(self):
		'''
		routine du client
		'''
		handlers = {
			'/exit': self._exit,
			'/quit': self._quit,
			'/join': self._join,
			'/send': self._send,
			'/myInfo': self._getInfo,
			'/joinServer': self._joinServer,
			'/askServer' : self._askServer
		}
		self.__running = True
		self.__address = None
		#threading.Thread(target=self._receive).start()#le thread s'arrete quelque part lors de l'execution si pas mis dans la boucle
		while self.__running:
			threading.Thread(target=self._receive).start()
			line = sys.stdin.readline().rstrip() + ' '
			command = line[:line.index(' ')]
			param = line[line.index(' ')+1:].rstrip()
			if command in handlers:
				try:
					handlers[command]() if param == '' else handlers[command](param)
				except:
					print("Erreur lors de l'execution de la commande.")
					traceback.print_exc(file=sys.stdout)
			else:
				print('Commande inconnue:', command)
	
	def _joinServer(self, param):
		'''
		permet de connecter le client au serveur
		
		pre :	param est un [str] de format : "ipAddress port"
		post :	se connecte au serveur
				envoie un message au serveur contenant les informations du client permettant
				une connexion p2p entre clients
		'''
		try:
			isAServer = True
			self.socketizer(isAServer) #initialise un socket stream
			self._join(param, isAServer) #connexion au serveur
			self._send(self.__name+'|_|'+str(self.__scPort), isAServer)# envoi des informations client
			self.__ss.shutdown(socket.SHUT_RDWR) #interrompt et empeche toute operation (read/write) ulterieure du socket stream
			self.__ss.close() #ferme le socket stream
			print(self.getInfo)
			#le port du socket stream utilise pour cette connexion (il est deja ferme au moment de l'affichage)
			#+les autres infos client
		except:
			self.__ss.close()
		
	def _askServer(self, param):
		'''
		permet d'envoyer une requete au serveur si une connexion a celui-ci a ete
		faite au prealable
		
		pre :	param est un [str] contenant "hostname" ou ".*"
		post :	envoie un message au serveur :
				"hostname" pour qu'il renvoie les informations de connexion p2p a hostname
				".*" pour qu'il renvoie la liste des clients connectes au serveur
		'''
		try:
			if self.__serverAddress is not None:
				isAServer = True
				self.socketizer(isAServer)
				self._join(self.__serverAddress, isAServer)
				self._send("askFor "+param, isAServer)
				self.__ss.shutdown(socket.SHUT_WR)
			else:
				print("Vous n'avez acces a aucun serveur")
		except:
			self.__ss.close()
	
	def _exit(self):
		'''
		termine le programme en se deconnectant du serveur et en fermant
		tous les sockets
		'''
		self.__running = False
		self._quit()
		try:
			self.__ss.close()
		except:
			pass
		try:
			self.__sc.close()
		except:
			pass
			
	def _quit(self):
		'''
		annule toutes les connexions en court (serveur et client)
		
		pre :	-
		post :	envoie un message au serveur lui indiquant qu'on souhaite enlever
				les informations du client de sa base de donnees
				oublie les addresses du serveur et du client eventuellement enregistrees
		'''
		try:
			isAServer = True
			self.socketizer(isAServer)
			self._join(self.__serverAddress, isAServer)
			self._send(self.__name+'|-|'+str(self.__scPort), isAServer)
			self.__ss.shutdown(socket.SHUT_RDWR)
			self.__ss.close()
			print("Vous etes deconnecte du serveur")
		except:
			self.__ss.close()
			print("La deconnection a echoue")
			traceback.print_exc(file=sys.stdout)
			
		self.__address = None
		self.__serverAddress = None
		
	def _join(self, param, isAServer=False):
		'''
		permet de se connecter a un serveur et d'enregistrer son adresse, ou
		d'enregistrer l'adresse d'un avec lequel on veut interagir
		
		pre :	param est un [str] de format : "ipAddress port"
				isAServer = True pour une connexion a un serveur
				isAServer = False pour un enregistrement d'adresse client
		post :	enregistre l'adresse fournie dans param
				si isAServer = True, se connecte a cette adresse
				si le port de connexion au serveur est dans un etat d'attente (il a ete ferme
				peu de temps auparavant et n'est pas encore accessible) Change automatiquement
				le port de connexion jusqu'a en trouver un accessible avec une limite
				imposee par self.__maxPortRange
				si cette limite est depassee, un message incitant a reesayer apres
				avoir attendu est envoye, et l'utilisateur devra entrer a nouveau sa commande
		'''
		tokens = param.split(' ')
		if len(tokens) == 2:
			try:
				self.__address = (socket.gethostbyname(tokens[0]), int(tokens[1]))
				if isAServer:
					self.__ss.connect(self.__address)
					self.__serverAddress = param
				print('Connecte a {}:{}'.format(*self.__address))
			except OSError as err:
				if not isinstance(isAServer, bool):
						isAServer = False
				if err.errno==10048 and self.__ssPort < self.__maxPortRange and isAServer:
					#si le port est deja utilise (ou en attente)
					self.__ssPort+=1
					self.socketizer(isAServer)
					self._join(param, isAServer)
				else:
					#si la connexion est impossible on reset le port
					#dans le but de recuperer un ancien port qui serait de nouveau accessible
					print("Erreur lors de la connexion, reessayez plus tard")
					self.__ssPort=self.__maxPortRange-998
				
	def _send(self, param, isAServer=False):
		'''
		envoie des donnees (param) au serveur ou au client connecte/enregistre
		
		pre :	param contient le message a envoyer
				isAServer = True pour un message a envoyer a un serveur (socket stream)
				isAServer = False pour un message a envoyer a un client (socket datagram)
		post :	envoie param par paquet de donnees selon la methode de reception de donnees du destinataire
		'''
		if self.__address is not None:
			try:
				message = param.encode()
				totalsent = 0
				while totalsent < len(message):
					if isAServer:
						sent = self.__ss.send(message[totalsent:])
					else:
						sent = self.__sc.sendto(message[totalsent:], self.__address)
					totalsent += sent
			except OSError:
				print("Erreur lors de l'envoi du message.")
				
	def _receive(self):
		'''
		receptionne des donnees
		
		pre :	-
		post :	teste d'abord de receptionner des donnees a partir du socket stream
				ferme le socket stream une fois les donnees receptionnees
				si cela echoue, tente de les receptionner a partir du socket datagram
		'''
		while self.__running:
			try:
				data, address = self.__ss.recvfrom(1024)
				message = data.decode()
				if message!='':
					self.__flagMessage = True
					print(message)
				else:
					if self.__flagMessage:
						self.__flagMessage = False
						self.__ss.close()
			except socket.timeout:
				pass
			except OSError:
				try:
					data, address = self.__sc.recvfrom(1024)
					print(data.decode())
				except socket.timeout:
					pass
				except OSError:
					return
	
	@property
	def getInfo(self):
		'''
		renvoie un tuple contenant hostname, ipAddress, le port de socket datagram, le port de
		socket stream
		'''
		return (self.__name, self.__ipAddress, self.__scPort, self.__ssPort)
			
	def _getInfo(self):
		'''
		affiche le tuple getInfo
		'''
		print(self.getInfo)
			
if __name__ == '__main__':
	'''
	launcher :	1x => server
				2x+=> clients
	le serveur sera sur le port 5000
	les clients seront sur les ports 5001 et/ou plus
	'''
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