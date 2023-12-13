import socket
import subprocess
import asyncio
import websockets
import json

#A faire:
#Toute la logique du jeu dans une fonction (appeler une pièce, tourner, envoyer les modifs...)
#L'host doit pouvoir lancer quand il veut et voir en temps réel le nombre de personnes connéctées.

my_number=0
async def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except OSError:
        return None

def show_menu():
    print("1. Host une partie")
    print("2. Rejoindre une partie")
    print("0. Quitter")
    
    try:
        choice = int(input("Entrez votre choix : "))
        return choice
    except ValueError:
        return -1

def start_server(local_ip):
    subprocess.Popen(['python', 'Server.py', local_ip, '4242'], creationflags=subprocess.CREATE_NEW_CONSOLE)

async def gameplay(websocket,turn):
    global my_number
    if(turn==my_number):
        # on joue normalement
    async for message in websocket:
        data = json.loads(message)
       
           

async def connect_to_server(local_ip):
    global my_number
    while True:
        uri = f"ws://{local_ip}:4242"
        async with websockets.connect(uri) as websocket:
            print(f"Connecté au serveur {local_ip}:4242 !")
            async for message in websocket:
                data = json.loads(message)
                if(data["action"]=="yourNumber"):
                    my_number=data["nb"]
                if(data["action"]=="NewConnexion"):
                    print("Nouvelle connexion, nombre de joueurs connecté: ",data["con"])
                    start_game = input("Voulez-vous démarrer la partie ? (o/n): ")
                    if start_game.lower() == "o":
                        await websocket.send(json.dumps({"action":"startGame"}))
                if(data["action"]=="startGame"):
                    print("On commence")
                # Vous pouvez ajouter ici d'autres actions en fonction des réponses du serveur

async def join_game():
    global my_number
    ip = input("Entrez l'adresse IP du serveur : ")
    port = input("Entrez le port du serveur : ")
    while True:
        uri = f"ws://{ip}:{port}"
        async with websockets.connect(uri) as websocket:
            print(f"Connecté au serveur {ip}:{port} !")
            print("")
            print("En attente de l'host")
            async for message in websocket:
                data = json.loads(message)
                if(data["action"]=="yourNumber"):
                    my_number=data["nb"]
                if(data["action"]=="NewConnexion"):
                    print("Nouvelle connexion, nombre de joueurs connecté: ",data["con"])
                if(data["action"]=="startGame"):
                    await gameplay(websocket,data["currentPlayer"])
                    print("bbbb")

async def main():
    while True:
        choice = show_menu()

        if choice == 0:
            print("Au revoir !")
            break
        elif choice == 1:
            local_ip = await get_local_ip()
            if local_ip:
                print(f"Adresse IP locale : {local_ip}")
                start_server(local_ip)
                await connect_to_server(local_ip)
            else:
                print("Impossible de récupérer l'adresse IP.")
        elif choice == 2:
            # Ajouter le code pour rejoindre une partie ici
            await join_game()
        else:
            print("Choix invalide. Veuillez réessayer.")

if __name__ == "__main__":
    asyncio.run(main())
