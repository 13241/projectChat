# projectChat
# author: Damien Abeloos

Cette application permet de chatter avec plusieurs utilisateurs connectes sur
un serveur lui aussi initialise par celle-ci.

Remarques
	
		le programme est configure pour faire des tests sur sa propre machine
	a partir d'une seule addresse IP, voir dans le code la remarque importante
	et les commentaires a modifier pour permettre un fonctionnement optimal de
	l'application entre plusieurs machines (non teste par manque de temps,
	mais ca devrait le faire :3)
		le programme a ete ecrit et teste dans et pour un environnement Windows 7, 
	pas de garantie de fonctionnement sur les autres systemes (non teste par manque
	de temps)

Utilisation

	executer appli.py pour lancer le serveur
	executer une seconde fois appli.py pour lancer un client
	executer autant de fois que desire appli.py pour lancer d'autres clients sur 
	votre machine

	en tant que client :

	1-) Connexion au serveur avec les parametres par defaut du programme :

		/joinServer xxx.xxx.xxx.xxx 5000
		
		ou xxx.xxx.xxx.xxx est l'adresse IP sur laquelle est connecte le serveur
		vous pouvez la trouver sur la deuxieme ligne de la console de commande qui 
		represente celui-ci (premiere application lancee : Server on ...)

	2-) Requete des noms des utilisateurs connectes au serveur : 

		/askServer .*
		
	3-) Requete des informations relatives a un nom d'utilisateur "hostname" obtenu
		a l'aide de la requete 2-)
		
		/askServer hostname
		
	4-) Connexion au client "hostname" dont vous avez obtenu l'addresse IP 
		xxx.xxx.xxx.xxx et le port XXXX
		
		/join xxx.xxx.xxx.xxx XXXX
		
	5-) Envoi d'un message au client "hostname" auquel vous vous etes connecte a 
		l'aide de la requete 4-)
		
		/send blblblblblblbl
		
	6-) Deconnexion du serveur et de "hostname", vos informations n'apparaitront 
		plus dans la base de donnees du serveur
		
		/quit
		
	7-) Affichage de vos informations personnelles

		/myInfo
		
	8-) Fin du programme

		/exit
		

Protocole de communication

	Client => Client : le client peut envoyer tout type de donnees convertibles en
	[str] a un autre client
	Serveur => Client : le serveur peut envoyer tout type de donnees convertibles 
	en [str] au client
	Client => Serveur : le client peut envoyer 3 formats de [str] au serveur, que
	celui-ci va pouvoir interpreter : 
	1-) "hostname|_|port" sans aucun espace indique que "hostname" veut se 
		connecter au serveur et que son port alloue a la communication 
		client/client est "port"
	2-) "hostname|-|port" sans aucun espace indique que "hostname" veut se
		deconnecter du serveur et que son port alloue a la communication 
		client/client est "port
	rem: pour ces deux cas, l'adresse ip est necessaire a la connexion au serveur
	celui-ci la connaissant deja, il est inutile de la lui respecifier.
	Aucun espace n'est permis dans ces commandes, y compris dans "hostname"
	3-) "command parameter" avec un espace entre la commande et son parametre
		indique au serveur que l'on veut effectuer la tache associee a la commande
		"command" et que les parametres necessaires a son execution sont dans
		"parameter"
	rem: dans notre application nous n'avons pas besoin de specifier plusieurs
	"command" l'utilisateur peut donc envoyer ce qu'il veut pour cet argument, 
	l'important est que les deux arguments soient separes par un espace
	
	les connexions client/client se font par le protocole UDP, en utilisant
	des socket datagram et des sequences de caracteres (encodage/decodage)
	
	les connexions client/serveur se font par le protocole TCP, en utilisant
	des socket stream et des sequences de caracteres (encodage/decodage)
		
	