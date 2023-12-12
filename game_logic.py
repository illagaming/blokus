import socket
import subprocess
import asyncio
import websockets

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

async def connect_to_server(local_ip):
    while True:
        uri = f"ws://{local_ip}:4242"
        async with websockets.connect(uri) as websocket:
            print(f"Connecté au serveur {local_ip}:4242 !")

            while True:
                # Attendre la réponse du serveur
                response = await websocket.recv()
                print(f"Nouvelle information du serveur : {response}")

                # Proposer de démarrer la partie ou effectuer d'autres actions en fonction de la réponse
                # Demander à l'utilisateur s'il veut démarrer la partie
                start_game = input("Voulez-vous démarrer la partie ? (o/n): ")
                if start_game.lower() == "o":
                    await websocket.send("Démarrer la partie")

                # Vous pouvez ajouter ici d'autres actions en fonction des réponses du serveur

async def join_game():
    ip = input("Entrez l'adresse IP du serveur : ")
    port = input("Entrez le port du serveur : ")

    uri = f"ws://{ip}:{port}"
    async with websockets.connect(uri) as websocket:
        print(f"Connecté au serveur {ip}:{port} !")

        while True:
            # Attendre la réponse du serveur
            response = await websocket.recv()
            print(f"Nouvelle information du serveur : {response}")


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
                input("Appuyez sur \"Entré\" pour vous connécter")
                await connect_to_server(local_ip)
            else:
                print("Impossible de récupérer l'adresse IP.")
        elif choice == 2:
            # Ajouter le code pour rejoindre une partie ici
            pass
        else:
            print("Choix invalide. Veuillez réessayer.")

if __name__ == "__main__":
    asyncio.run(main())
