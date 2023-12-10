# import asyncio
# import websockets
# import json
# import random

# async def connection_handler(websocket, path):
#     global clients, player_count, required_players, start_game_sent, player_number, starting_player

#     # Ajoute le client à la liste des clients connectés et incrémente le nombre de joueurs
#     clients.add(websocket)
#     player_count += 1

#     # Envoie un numéro de joueur à chaque nouveau client
#     if player_number <= required_players:
#         await websocket.send(json.dumps({"action": "givePlayerNumber", "number": player_number}))
#         player_number += 1

#     try:
#         async for message in websocket:
#             data = json.loads(message)

#             # Vérifie l'action "setPlayers" pour définir le nombre de joueurs requis
#             if data.get("action") == "setPlayers" and "players" in data:
#                 required_players = data["players"]

#                 # Vérifie si le nombre de joueurs requis est atteint pour démarrer le jeu
#                 if not start_game_sent and player_count >= required_players:
#                     # Choix aléatoire du joueur qui commence
#                     starting_player = random.randint(1, required_players)

#                     # Crée un message combiné pour "startGame" et "currentPlayer" et l'envoie à tous les clients
#                     start_game_message = {
#                         "action": "startGame",
#                         "currentPlayer": starting_player
#                     }
#                     await asyncio.wait([client.send(json.dumps(start_game_message)) for client in clients])
#                     start_game_sent = True

#             # Relaie tous les autres messages à tous les clients connectés
#             await asyncio.wait([client.send(message) for client in clients if client != websocket])
#     finally:
#         # Décrémente le nombre de joueurs lorsque quelqu'un se déconnecte et le retire de la liste des clients
#         player_count -= 1
#         clients.remove(websocket)

# async def start_server(ip, port):
#     global clients, player_count, required_players, start_game_sent, player_number, starting_player

#     # Initialisation des variables pour le serveur
#     required_players = 0
#     player_count = 0
#     clients = set()
#     start_game_sent = False
#     player_number = 1
#     starting_player = 0

#     # Démarre le serveur WebSocket et attend les connexions
#     async with websockets.serve(connection_handler, ip, port):
#         await asyncio.Future()

# # Exécute le serveur avec l'adresse IP et le port spécifiés
# asyncio.run(start_server("172.20.10.6", 4242))
import asyncio
import websockets
import sys

async def server(ip, port):
    async with websockets.serve(handler, ip, port):
        print(f"Serveur démarré à l'adresse {ip} sur le port {port}")
        await asyncio.Future()  # Maintien du serveur ouvert

async def handler(websocket, path):
    print("Nouvelle connexion établie.")

    try:
        async for message in websocket:
            # Traiter les messages reçus ici
            pass
    finally:
        print("Connexion terminée.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python Serveur.py [adresse IP] [port]")
    else:
        ip = sys.argv[1]
        port = int(sys.argv[2])
        asyncio.run(server(ip, port))
