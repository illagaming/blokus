import os
import sys
import websockets
import asyncio
import json

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
        self.is_host = False
        self.websocket = None
        self.clients = set()
        self.debug = True

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

        os.system('cls' if os.name == 'nt' else 'clear') 

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
        os.system("cls" if os.name == 'nt' else 'clear')
        display_tab = [row.copy() for row in self.board]
        color_code = self.player_colors[self.current_player]
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
                    self.board[i + x][j + y] = f"{self.player_colors[self.current_player]}#\033[0m" 
                    asyncio.create_task(self.send_update_to_all_clients())
        
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

    ### Méthodes WebSocket ###

    # Host
    async def host_game(self, ip, port):
        self.is_host = True
        self.current_player = 1
        player_number = 2

        print(f"En attente de {self.number_of_players - 1} joueurs...")

        async def connection_handler(websocket, path):
            nonlocal player_number
            self.clients.add(websocket)
            print(f"Joueur {player_number} connecté.")
            await websocket.send(json.dumps({'action': 'assign_number', 'number': player_number}))
            player_number += 1

            if len(self.clients) == self.number_of_players - 1:
                print("Tous les joueurs sont connectés. Le jeu peut commencer.")
                await self.main()  # Démarrer le jeu

            try:
                async for message in websocket:
                    data = json.loads(message)
                    if data['action'] == 'move':
                        await self.process_client_move(data, player_number)
                        
            finally:
                self.clients.remove(websocket)
                print(f"Joueur {player_number} déconnecté.")

        try:
            async with websockets.serve(connection_handler, ip, port):
                await asyncio.Future()
        except:
            print("Erreur: Port Indisponible ou Adresse IP incorrecte.")

    # Client
    async def connect_to_game(self, ip, port):
        self.is_host = False
        uri = f"ws://{ip}:{port}"
        try:
            async with websockets.connect(uri) as websocket:
                self.websocket = websocket
                print("Connecté au serveur. En attente des autres joueurs...")
                async for message in websocket:
                    data = json.loads(message)
                    if data['action'] == 'update':
                        self.board = data['board']
                        self.current_player = data['current_player']
                        # Afficher le plateau de jeu
                        self.display_board(self.blokus_pieces[self.current_piece_key][self.rotation_idx], self.x, self.y)
                        if self.current_player == self.my_player_number:
                            await self.main()  # Tour de ce client pour jouer
                    elif data['action'] == 'assign_number':
                        self.my_player_number = data['number']
                        print(f"Vous êtes le joueur {self.my_player_number}.")
        except:
            print("Erreur de connexion au serveur. Vérifiez l'adresse IP et le port.")

    async def send_update_to_all_clients(self):
        update = json.dumps({'action': 'update', 'board': self.board, 'current_player': self.current_player})
        await asyncio.gather(*(client.send(update) for client in self.clients))

    ### Principal code du jeu

    def show_menu(self):
        """"Affiche le menu du joueur"""
        os.system('cls' if os.name == 'nt' else 'clear')
        print("********** Menu **********")
        print("1. Héberger une partie")
        print("2. Se connecter à une partie")
        print("3. Quitter")
        try:
            return int(input("Entrez votre choix : "))
        except ValueError:
            return 0  # Retourner une valeur non valide en cas d'erreur
    
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
        """
        Initialisation du jeu. Cette méthode prépare le plateau de jeu, sélectionne les pièces,
        et définit le nombre de joueurs.
        """
        os.system("cls" if os.name == 'nt' else 'clear')

        # self.set_number_of_players()      

        # Création du plateau de jeu, sélection des pièces, etc.
        self.tab = self.crea_tab()  
        self.current_piece_key = self.choose_piece()  # Méthode pour choisir la première pièce
        self.rotation_idx = 0  # Index de la rotation actuelle pour la pièce choisie
        self.x, self.y = 1, 1  # Positions initiales sur le plateau
    
    async def main(self):
        self.initialize_game()
        all_players_blocked = False

        while not all_players_blocked:
            if not self.player_can_play(self.current_player):
                print(f"Le joueur {self.current_player} est bloqué et passe son tour.")
                all_players_blocked = all(
                    not self.player_can_play(player) for player in range(1, self.number_of_players + 1)
                )
                if all_players_blocked:
                    break

                self.current_player = (self.current_player % self.number_of_players) + 1
                if self.is_host:
                    # Mettre à jour et envoyer l'état actuel du jeu à tous les clients
                    update = json.dumps({'action': 'update', 'board': self.board, 'current_player': self.current_player})
                    await asyncio.gather(*(client.send(update) for client in self.clients))
                continue

            # Afficher le plateau de jeu
            self.send_update_to_all_clients()
            self.display_board(self.blokus_pieces[self.current_piece_key][self.rotation_idx], self.x, self.y)

            if self.is_host or self.current_player == self.my_player_number:
                # Si c'est le tour du joueur
                print(f"Tour du joueur {self.current_player}.")
                key_pressed = self.get_key()

                if key_pressed == 'k':
                    print("Fin du jeu...")
                    break

                self.x, self.y, self.rotation_idx = self.modify_board(
                    self.current_piece_key, self.x, self.y, key_pressed, self.rotation_idx)
                self.display_board(self.blokus_pieces[self.current_piece_key][self.rotation_idx], self.x, self.y)

                if key_pressed in ('\r', '\n'):
                    current_piece = self.blokus_pieces[self.current_piece_key][self.rotation_idx]
                    current_x = self.x
                    current_y = self.y

                    if self.can_place_piece(current_piece, current_x, current_y):
                        self.place_piece(current_piece, current_x, current_y)
                        self.update_score()

                        # Passer au joueur suivant
                        self.current_player = (self.current_player % self.number_of_players) + 1
                        self.current_piece_key = self.choose_piece()
                        self.rotation_idx = 0
                        self.x, self.y = 1, 1

                        # Mettre à jour le plateau pour tous les clients
                        if self.is_host:
                            update = json.dumps({'action': 'update', 'board': self.board, 'current_player': self.current_player})
                            await asyncio.gather(*(client.send(update) for client in self.clients))
                        elif self.websocket:
                            await self.send_action_to_server('move', key_pressed)
            else:
                print("En attente du tour des autres joueurs...")
                await asyncio.sleep(0.1)  # Petite pause pour éviter la surcharge CPU

        # Calcul des scores finaux
        self.calculate_final_scores()
        print("Scores finaux :")
        for player, score in self.scores.items():
            print(f"Joueur {player}: {score} points")


    def run(self):
        """
        Cette méthode gère le menu principal et les sélections d'options.
        """
        while True:
            user_choice = self.show_menu()
            if user_choice == 1:
                # ip = input("Entrez l'adresse IP pour l'hôte : ")
                # port = input("Entrez le port : ")
                asyncio.run(self.host_game("172.20.10.6", "4242"))
            elif user_choice == 2:
                ip = input("Entrez l'adresse IP de l'hôte : ")
                port = input("Entrez le port : ")
                asyncio.run(self.connect_to_game("172.20.10.6", "4242"))
            elif user_choice == 3:
                print("Au revoir!")
                break
            else:
                print("Option invalide, veuillez réessayer.")
            
            input("Appuyez sur entrer pour continuer...")  # Pause avant de nettoyer l'écran  
    
# Pour démarrer le jeu, vous créez une instance de votre jeu et appelez 'run'.
if __name__ == "__main__":
    game = BlukusGame()
    game.run()