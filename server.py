import asyncio
import websockets
import json
import random
import sys

# Partie de gestion des connexions clients

async def handler(websocket, path):
    global clients, player_count, required_players, start_game_sent, player_number, starting_player
    
    # Nouvelle connexion établie
    print("Nouvelle connexion établie.")
    
    # Ajout du client à la liste des clients
    clients.append(websocket)
    
    # Incrémentation du nombre de joueurs
    player_count += 1
    
    # Envoi du nombre du joueur au client
    await websocket.send(json.dumps({"action": "yourNumber", "nb": player_count}))
    
    # Envoi à tous les clients du nombre total de connexions actives
    await clients[0].send(json.dumps({"action": "NewConnexion", "con": player_count}))
    
    try:
        async for message in websocket:
            data = json.loads(message)
            
            # Traitement des messages reçus
            
            # Vérification de l'action "startGame" pour démarrer le jeu
            if data.get("action") == "startGame":
                
                # Vérifie si le jeu n'a pas déjà été lancé
                if not start_game_sent:
                    # Choix aléatoire du joueur qui commence
                    starting_player = random.randint(1, len(clients))
                    
                    # Création du message "startGame" et envoi à tous les clients
                    start_game_message = {
                        "action": "startGame",
                        "currentPlayer": starting_player,
                        "players": len(clients)
                    }
                    print(start_game_message)
                    
                    # Envoi du message à tous les clients
                    await asyncio.gather(*[client.send(json.dumps(start_game_message)) for client in clients])
                    start_game_sent = True
            
            # Relayage de tous les autres messages à tous les clients connectés
            if data.get("action") == "test":
                await websocket.send(json.dumps({"action": "test"}))
            else:
                await asyncio.gather(*[client.send(message) for client in clients if client != websocket])

    finally:
        print("Connexion terminée.")
        # Code pour gérer la déconnexion d'un client
        #player_count -= 1
        #clients.pop(websocket)

# Partie du serveur

async def server(ip, port):
    global clients, player_count, required_players, start_game_sent, player_number, starting_player
    
    # Initialisation des variables pour le serveur
    required_players = 0
    player_count = 0
    clients = []
    start_game_sent = False
    player_number = 1
    starting_player = 0
    
    # Création du serveur WebSocket
    async with websockets.serve(handler, ip, port):
        print(f"Serveur démarré à l'adresse {ip} sur le port {port}")
        await asyncio.Future()  # Maintien du serveur ouvert

# Exécution du serveur

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python Serveur.py [adresse IP] [port]")
    else:
        ip = sys.argv[1]
        port = int(sys.argv[2])
        asyncio.run(server(ip, port))
