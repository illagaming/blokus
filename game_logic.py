import socket
import subprocess
import asyncio
import websockets
import json
import os
import sys

#A faire:
#Toute la logique du jeu dans une fonction (appeler une pièce, tourner, envoyer les modifs...)
#L'host doit pouvoir lancer quand il veut et voir en temps réel le nombre de personnes connéctées.
# Importez la bibliothèque appropriée en fonction du système d'exploitation
if sys.platform.startswith('linux'):
    try:
        import readchar
    except ImportError:
        raise ImportError("Vous devez installer la bibliothèque readchar pour les systèmes Linux.")
elif sys.platform.startswith('win'):
    import msvcrt
else:
    raise OSError("Ce script ne supporte que Windows et Linux.")

class BlukusGame:
    def __init__(self):
        self.board = self.crea_tab()
        self.current_player = 1
        self.turn_count = 1
        self.players = {1: [], 2: [], 3: [], 4: []}  # Chaque joueur a une liste de pièces utilisées.
        self.available_pieces = {
            "I1": [
                ["#"]
            ],
            "I2": [
                ["#", "#"]
            ],
            "I3": [
                ["#", "#", "#"]
            ],
            "I4": [
                ["#", "#", "#", "#"]
            ],
            "I5": [
                ["#", "#", "#", "#", "#"]
            ],
            "L4": [
                ["#", "#", "#"],
                ["#", " ", " "]
            ],
            "L5": [
                ["#", "#", "#", "#"],
                ["#", " ", " ", " "]
            ],
            "V3": [
                ["#", "#"],
                ["#", " "]
            ],
            "V5": [
                ["#", "#", "#"],
                ["#", " ", "#"]
            ],
            "N": [
                ["#", "#", " "],
                [" ", "#", "#"]
            ],
            "Y": [
                [" ", "#"],
                ["#", "#"],
                [" ", "#"]
            ],
            "T": [
                ["#", "#", "#"],
                [" ", "#", " "]
            ],
            "Z4": [
                ["#", "#"],
                [" ", "#"],
                [" ", "#"]
            ],
            "Z5": [
                [" ", " ", "#"],
                ["#", "#", "#"],
                ["#", " ", " "]
            ],
            "U": [
                ["#", " ", "#"],
                ["#", "#", "#"]
            ],
            "F": [
                [" ", "#", "#"],
                ["#", "#", " "],
                [" ", "#", " "]
            ],
            "W": [
                ["#", " ", " "],
                ["#", "#", " "],
                [" ", "#", "#"]
            ],
            "P": [
                ["#", "#"],
                ["#", "#"],
                ["#", " "]
            ],
            "X": [
                [" ", "#", " "],
                ["#", "#", "#"],
                [" ", "#", " "]
            ],
            "O4": [
                ["#", "#"],
                ["#", "#"]
            ],
            "O5": [
                ["#", "#", "#"],
                ["#", "#", " "]
            ]
        }
        self.player_colors = {
            1: '\033[92m',  # Vert
            2: '\033[91m',  # Rouge
            3: '\033[34m',  # Bleu
            4: '\033[93m'   # Jaune
        }
        self.blokus_pieces = self.initialize_pieces()  # Génère toutes les rotations possibles pour chaque pièce
        self.rotation_idx = 0
        self.x, self.y = 1, 1
        self.number_of_players = 2 # Par défaut
        self.scores = {1: 0, 2: 0, 3: 0, 4: 0}  # Initialise les scores pour chaque joueur
        self.debug = False
        self.tab = self.crea_tab()
    def get_key(self):
        """Récupère la touche pressée par l'utilisateur"""
        if sys.platform.startswith('linux'):
            # Utilisez readchar pour les systèmes Linux
            return readchar.readkey()
        elif sys.platform.startswith('win'):
            # Utilisez msvcrt pour les systèmes Windows
            return msvcrt.getch().decode('utf-8', errors="ignore")

    def rotate(self, piece):
        """Fait pivoter la pièce de 90 degrés"""
        transposed = [list(row) for row in zip(*piece)]
        return [row[::-1] for row in transposed]

    def generate_rotations(self, piece):
        """Génère toutes les rotations possibles pour une pièce donnée"""
        rotations = [piece]
        for _ in range(3):
            rotations.append(self.rotate(rotations[-1]))
        return rotations

    def initialize_pieces(self):
        """Initialise les pièces du jeu avec toutes les rotations possibles."""
        blokus_pieces = {}
        for key, piece in self.available_pieces.items():
            blokus_pieces[key] = self.generate_rotations(piece)
        return blokus_pieces
   
    def limit_pieces(self):
        """Limite le nombre de pièces par utilisateur."""
        for player, pieces in self.players.items():
            available_pieces = self.available_pieces.copy()  
            for piece in pieces:
                if piece in available_pieces:
                    del available_pieces[piece]  # Supprime la pièce utilisée des pièces disponibles
            self.players[player] = available_pieces  # Met à jour les pièces disponibles pour le joueur

    def choose_piece(self):
        """
        Permet au joueur de choisir une pièce parmi celles disponibles, en excluant celles déjà utilisées.
        """
        # Récupérer les pièces encore disponibles pour le joueur actuel
        available_pieces = [p for p in self.available_pieces if p not in self.players[self.current_player]]

        #os.system('cls' if os.name == 'nt' else 'clear')

        # Afficher les pièces disponibles pour la sélection
        print("Pièces disponibles :")
        for index, piece in enumerate(available_pieces, 1):
            print(f"{index}: {piece}")

        # Boucle jusqu'à ce que le joueur fasse un choix valide
        while True:
            try:
                choice = input("Entrez le numéro de la pièce que vous souhaitez utiliser : ")
                choice = int(choice)

                if 1 <= choice <= len(available_pieces):
                    selected_piece = available_pieces[choice - 1]

                    # Ajouter la pièce sélectionnée à la liste des pièces utilisées par le joueur
                    self.players[self.current_player].append(selected_piece)
                    return selected_piece  # Retourner la pièce sélectionnée
                else:
                    print("Sélection non valide. Veuillez choisir un numéro de la liste.")
            except ValueError:
                print("Veuillez entrer un nombre valide.")


    def crea_tab(self):
        tab = [['*'] * 22 for _ in range(22)]
        for i in range(1, 21):
            for j in range(1, 21):
                tab[i][j] = ' '    
        return tab

    def display_board(self, piece, x, y):
        #os.system("cls" if os.name == 'nt' else 'clear')
        display_tab = [row.copy() for row in self.board]
        color_code = self.player_colors[1]
        piece_char = color_code + '#\033[0m'

        # Débug placement pièces
        if self.debug == True :
            if self.turn_count == 1:
                print(f"Est dans un coin : {self.is_corner(piece, x, y)}")
                print(f"Premire tour : {self.is_first_turn()}")
            print(f"Diagonale : {self.is_adjacent_to_same_color(piece,x,y)}")
            print(f"Latéral : {self.can_place_without_side_contact(piece,x,y)}")
            print(f"Tour actuel : {self.turn_count}")

        try:
            # Parcourir la pièce et ajouter la pièce à la copie du tableau à afficher.
            for i in range(len(piece)):
                for j in range(len(piece[i])):
                    if piece[i][j] == "#":
                        # S'assurer que nous ne sortons pas des limites du tableau.
                        if 0 <= i + x < len(display_tab) and 0 <= j + y < len(display_tab[i + x]):
                            display_tab[i + x][j + y] = piece_char
                        else:
                            # Si la pièce dépasse les limites, le programme ne tente pas de la placer et affiche une erreur ou avertissement si nécessaire.
                            pass  # Vous pouvez également gérer une erreur ou un avertissement ici si vous le souhaitez.
        except IndexError:
            # Gérer les erreurs d'index si quelque chose ne va pas lors du placement de la pièce.
            print("Une erreur est survenue lors de l'affichage de la pièce sur le plateau.")

        # Afficher le tableau mis à jour.
        for row in display_tab:
            print(' '.join(row))

    def place_piece(self, piece, x, y):
        """Place la pièce sur le tableau et met à jour le statut du joueur."""
        for i in range(len(piece)):
            for j in range(len(piece[i])):
                if piece[i][j] == "#":
                    self.board[i + x][j + y] = f"{self.player_colors[self.current_player]}#\033[0m"  # Ou simplement '#' selon votre logique de jeu

        # Ajoutez la pièce à la liste des pièces utilisées pour ce joueur
        self.players[self.current_player].append(self.current_piece_key)
   
    def can_place_piece(self, piece, x, y):
        """"Vérifie si l'on peut placer la pièce sur le plateau"""
        if self.is_corner(piece, x, y) and self.is_first_turn() == True:
            for i in range(len(piece)):
                for j in range(len(piece[i])):
                    if piece[i][j] == "#" and self.board[i + x][j + y] != ' ':
                        return False
            return True

        if self.is_adjacent_to_same_color(piece, x, y) and not self.is_first_turn() and self.can_place_without_side_contact(piece,x,y):
            for i in range(len(piece)):
                for j in range(len(piece[i])):
                    if piece[i][j] == "#" and self.board[i + x][j + y] != ' ':
                        return False
            return True      

    def can_move_to(self, piece, x, y):
        for i in range(len(piece)):
            for j in range(len(piece[i])):
                if piece[i][j] == "#":
                    if i + x < 0 or i + x >= len(self.board) or j + y < 0 or j + y >= len(self.board[0]):
                        return False
        return True

    def modify_board(self, current_piece_key, x, y, key_pressed, rotation_idx):
        piece = self.blokus_pieces[current_piece_key][rotation_idx]
        if key_pressed == 'z' and self.can_move_to(piece, x - 1, y):
            x -= 1
        elif key_pressed == 's' and self.can_move_to(piece, x + 1, y):
            x += 1
        elif key_pressed == 'q' and self.can_move_to(piece, x, y - 1):
            y -= 1
        elif key_pressed == 'd' and self.can_move_to(piece, x, y + 1):
            y += 1
        elif key_pressed in ('a', 'e'):
            new_rotation_idx = (rotation_idx + (1 if key_pressed == 'e' else -1)) % 4
            new_piece = self.blokus_pieces[current_piece_key][new_rotation_idx]
            if self.can_move_to(new_piece, x, y):
                rotation_idx = new_rotation_idx

        return x, y, rotation_idx

    def is_first_turn(self):
        """Vérifie si c'est le premier tour du joueur."""
        return len(self.players[self.current_player]) == 1

    def is_corner(self, piece, x, y):
        """"Vérifie si la première pièce placée par chaque joueur est dans un coin"""
        corners = [(1, 1), (1, 20), (20, 1), (20, 20)]
        for i in range(len(piece)):
            for j in range(len(piece[i])):
                if piece[i][j] == "#":
                    piece_x, piece_y = x + i, y + j
                    if (piece_x, piece_y) in corners:
                        return True
        return False

    def is_adjacent_to_same_color(self, piece, x, y):
        """Vérifie si au moins un coin de la pièce est correctement adjacent par les coins à une pièce de même couleur."""
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]  # Diagonales
        for i in range(len(piece)):
            for j in range(len(piece[i])):
                if piece[i][j] == "#":
                    # Vérifie l'adjacence pour chaque coin de la pièce
                    for dx, dy in directions:
                        nx, ny = x + i + dx, y + j + dy
                        if 0 <= nx < len(self.board) and 0 <= ny < len(self.board[0]):
                            if self.board[nx][ny].startswith(self.player_colors[self.current_player]):
                                return True  # Adjacence valide trouvée
        return False  # Aucune adjacence valide trouvée

    def can_place_without_side_contact(self, piece, x, y):
        """Vérifie si la pièce peut être placée sans toucher les côtés d'une pièce de la même couleur."""
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # Haut, Bas, Gauche, Droite
        for i in range(len(piece)):
            for j in range(len(piece[i])):
                if piece[i][j] == "#":
                    # Vérifie le contact latéral pour chaque segment de la pièce
                    for dx, dy in directions:
                        nx, ny = x + i + dx, y + j + dy
                        if 0 <= nx < len(self.board) and 0 <= ny < len(self.board[0]):
                            if self.board[nx][ny].startswith(self.player_colors[self.current_player]):
                                return False  # Contact latéral non autorisé trouvé
        return True  # Aucun contact latéral non autorisé
   
    def update_score(self):
        """ Met à jour le score du joueur courant en fonction des pièces non placées. """
        pieces_non_placees = set(self.available_pieces.keys()) - set(self.players[self.current_player])
        squares_unplaced = sum(sum(len(row) for row in self.available_pieces[piece]) for piece in pieces_non_placees)
        # Mettre à jour le score
        if len(self.players[self.current_player]) == 21:
            # Bonus pour avoir placé toutes les pièces
            self.scores[self.current_player] += 20 if self.players[self.current_player][-1] == "I1" else 15
        else:
            # Pénalité pour les pièces non placées
            self.scores[self.current_player] -= squares_unplaced

    def player_can_play(self, player):
        """ Vérifie si le joueur peut placer une pièce. """
        # Récupérer les pièces encore disponibles pour le joueur donné
        available_pieces = [p for p in self.available_pieces if p not in self.players[player]]

        for piece_key in available_pieces:
            piece = self.available_pieces[piece_key]
            for rotation in self.generate_rotations(piece):
                for x in range(1, 21):
                    for y in range(1, 21):
                        if self.can_place_piece(rotation, x, y):
                            return True
        return False
   
    def calculate_final_scores(self):
        """ Calcule les scores finaux pour tous les joueurs. """
        for player in range(1, self.number_of_players + 1):
            self.current_player = player
            self.update_score()
           
    def set_number_of_players(self):
        """"Permet de choisir le nombre de joueurs de l'application"""
        print(f"Nombre de joueurs par défaut : {self.number_of_players}")

        while True:
            change = input("Voulez-vous changer le nombre de joueurs ? (y/n): ").strip().lower()
            if change == 'y':
                while True:
                    try:
                        number = int(input("Entrez le nombre de joueurs (2-4): ").strip())
                        if 2 <= number <= 4:
                            self.number_of_players = number
                            return  # Sortie de la fonction après une saisie valide
                        else:
                            print("S'il vous plaît, entrez un nombre valide de joueurs (2-4).")
                    except ValueError:
                        print("Entrée invalide. Veuillez entrer un nombre.")
            elif change == 'n':
                return  # Sortie de la fonction si l'utilisateur ne souhaite pas changer le nombre de joueurs
            else:
                print("Réponse non valide. Veuillez répondre par 'y' (oui) ou 'n' (non).")

    def initialize_game(self):
        """Initialise les paramètres et l'état du jeu avant de commencer une nouvelle partie"""
        #os.system("cls" if os.name == 'nt' else 'clear')    
        
        self.current_piece_key = self.choose_piece()
        self.rotation_idx = 0
        self.x, self.y = 1, 1
    
#  __  __       _      
# |  \/  |     (_)      
# | \  / | __ _ _ _ __  
# | |\/| |/ _` | | '_ \
# | |  | | (_| | | | | |
# |_|  |_|\__,_|_|_| |_|



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

async def gameplay(websocket,turn,game):
    pieceChoosed=False
    while True:
        if(turn==my_number):
            if(pieceChoosed==False):
                game.initialize_game()
                pieceChoosed==True
            if not game.player_can_play(game.current_player):
                print(f"Le joueur {game.current_player} est bloqué et passe son tour.")

                # Vérifier si tous les joueurs sont bloqués
                all_players_blocked = all(
                    not game.player_can_play(player) for player in range(1, game.number_of_players + 1)
                )

                if all_players_blocked:
                    print("Tous les joueurs sont bloqués. Fin du jeu.")
                    break

                # Passer au joueur suivant
                game.current_player = (game.current_player % game.number_of_players) + 1
                continue

            # Afficher le plateau avec la pièce actuelle
            game.display_board(game.blokus_pieces[game.current_piece_key][game.rotation_idx], game.x, game.y)
            await websocket.send(json.dumps({"action":"display","blockus_pieces":game.blokus_pieces[game.current_piece_key][game.rotation_idx],"x":game.x,"y":game.y}))
            # Instructions pour le joueur actuel
            print(f"Tour du joueur {game.current_player}. Utilisez z, q, s, d pour déplacer la pièce, 'a' pour la tourner à gauche, 'e' pour la tourner à droite, 'ENTRÉE' pour la placer. Appuyez sur 'k' pour quitter.")
            key_pressed = game.get_key()  # Lecture de l'entrée du clavier

            if key_pressed == 'k':  # Condition pour quitter le jeu
                print("Fin du jeu...")
                break

            # Traitement de l'action de placement de la pièce
            print(key_pressed)
            if key_pressed in ('\r', '\n'):
                current_piece = game.blokus_pieces[game.current_piece_key][game.rotation_idx]
                current_x = game.x
                current_y = game.y

                # Vérifier si la pièce peut être placée à cet endroit
                if game.can_place_piece(current_piece, current_x, current_y):
                    game.place_piece(current_piece, current_x, current_y)  # Placer la pièce

                    # Mettre à jour le score
                    game.update_score()

                    # Passer au joueur suivant
                    game.current_player = (game.current_player % game.number_of_players) + 1
        
                    game.rotation_idx = 0  # Réinitialiser la rotation pour la nouvelle pièce
                    game.x, game.y = 1, 1  # Réinitialiser les positions
                else:
                    print("Action impossible. Vous ne pouvez pas placer la pièce ici.")
            else:
                # Traitement des autres actions (déplacement, rotation)
                game.x, game.y, game.rotation_idx = game.modify_board(
                    game.current_piece_key, game.x, game.y, key_pressed, game.rotation_idx)
        else:
            pieceChoosed==False
            async for message in websocket:
                data = json.loads(message)
                if(data["action"]=="display"):
                    game.display_board(data['blockus_pieces'],data["x"], data["y"])
           

async def connect_to_server(local_ip):
    global my_number
    while True:
        uri = f"ws://{local_ip}:4242"
        async with websockets.connect(uri) as websocket:
            print(f"Connecté au serveur {local_ip}:4242 !")
            async for message in websocket:
                data = json.loads(message)
                print(data)
                if(data["action"]=="yourNumber"):
                    my_number=data["nb"]
                if(data["action"]=="NewConnexion"):
                    print("Nouvelle connexion, nombre de joueurs connecté: ",data["con"])
                    start_game = input("Voulez-vous démarrer la partie ? (o/n): ")
                    if start_game.lower() == "o":
                        await websocket.send(json.dumps({"action":"startGame"}))
                if(data["action"]=="startGame"):
                    await gameplay(websocket,data["currentPlayer"],game)
                # Vous pouvez ajouter ici d'autres actions en fonction des réponses du serveur

async def join_game(game):
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
                data = json.loads(message)
                if(data["action"]=="yourNumber"):
                    my_number=data["nb"]
                if(data["action"]=="NewConnexion"):
                    print("Nouvelle connexion, nombre de joueurs connecté: ",data["con"])
                if(data["action"]=="startGame"):
                    await gameplay(websocket,data["currentPlayer"],game)
                    print("bbbb")

async def main(game):
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
            await join_game(game)
        else:
            print("Choix invalide. Veuillez réessayer.")

if __name__ == "__main__":
    game = BlukusGame()
    asyncio.run(main(game))
