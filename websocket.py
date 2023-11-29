import asyncio
import json
import subprocess  
from websockets.server import serve
from websockets.sync.client import connect

clients = set()  
#Côté hôte  
async def hostgame(websocket):
    global clients
    clients.add(websocket)
    try:
        async for message in websocket:
            # Transmettre le message à tous les autres clients
            if(message.action=="print"):
                for client in clients:
                    if client != websocket:
                        await client.send(message)
                #Afficher l'écran de jeu
                print("Attendez votre tour")
                print(message.tab)
            elif(message.action=="endTurn"):
                for client in clients:
                    if client != websocket:
                        await client.send(message)
                #Afficher l'écran de jeu
                print(message.tab)
                if(message.turn-1==3):
                    #A mon tour de jouer, faire toutes les étapes (a chaque déplacement, j'envoie le nouveau tableau)
                else:
                    #Je dis a qui c'est le tour de jouer
                    client=clients[message.turn-1]
                    message={"action":"yourTurn"}
                    message = json.dumps(message)
                    await client.send(message)
    finally:
        # Enlever le client de la liste lorsqu'il se déconnecte
        clients.remove(websocket)
   
async def host(ip,port):
     async with serve(hostgame, ip, port, max_size=3):
        await asyncio.Future()  # run forever

#Côté client
def connect(ip,port):
    with connect("ws://"+ ip +":"+port) as websocket:
        message = websocket.recv()
        if(message.action=="print"):
            #Afficher l'écran de jeu
            print("Attendez votre tour")
            print(message.tab)
        elif(message.action=="yourTurn"):
            #A mon tour de jouer, faire toutes les étapes (a chaque déplacement, j'envoie le nouveau tableau)