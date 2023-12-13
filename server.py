

import asyncio
import websockets
import json
import random
import sys



async def handler(websocket, path):
    global clients, player_count, required_players, start_game_sent, player_number, starting_player
    print("Nouvelle connexion établie.")
    clients.append(websocket)
    player_count += 1
    await websocket.send(json.dumps({"action":"yourNumber","nb":player_count}))
    await clients[0].send(json.dumps({"action":"NewConnexion","con":player_count}))
    try:
        async for message in websocket:
            data = json.loads(message)
            # Traiter les messages reçus ici
             # Vérifie l'action "setPlayers" pour définir le nombre de joueurs requis
            if data.get("action") == "startGame":

                 # Vérifie si le nombre de joueurs requis est atteint pour démarrer le jeu
                if not start_game_sent:
                    # Choix aléatoire du joueur qui commence
                    starting_player = random.randint(1, len(clients))

                    # Crée un message combiné pour "startGame" et "currentPlayer" et l'envoie à tous les clients
                    start_game_message = {
                        "action": "startGame",
                         "currentPlayer": starting_player
                     }
                    await asyncio.wait([client.send(json.dumps(start_game_message)) for client in clients])
                    start_game_sent = True

            # Relaie tous les autres messages à tous les clients connectés
            else:
                await asyncio.wait([client.send(message) for client in clients if client != websocket])
    finally:
        print("Connexion terminée.")
        # Décrémente le nombre de joueurs lorsque quelqu'un se déconnecte et le retire de la liste des clients
#         player_count -= 1
#         clients.remove(websocket)


async def server(ip, port):
    global clients, player_count, required_players, start_game_sent, player_number, starting_player

    # Initialisation des variables pour le serveur
    required_players = 0
    player_count = 0
    clients = []
    start_game_sent = False
    player_number = 1
    starting_player = 0

    async with websockets.serve(handler, ip, port):
        print(f"Serveur démarré à l'adresse {ip} sur le port {port}")
        await asyncio.Future()  # Maintien du serveur ouvert

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python Serveur.py [adresse IP] [port]")
    else:
        ip = sys.argv[1]
        port = int(sys.argv[2])
        asyncio.run(server(ip, port))
