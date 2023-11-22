import os
import sys

class BlukusGame:
    def __init__(self):
        self.board = self.crea_tab()
        self.current_player = 1
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

    def get_key(self):
        """Récupère la touche pressée par l'utilisateur"""
        # if sys.platform.startswith('linux'):
        #     # Pour Linux, utilisez la bibliothèque readchar ou une autre solution
        #     import readchar  # Vous devez peut-être installer cette bibliothèque
        #     return readchar.readkey()
        # elif sys.platform.startswith('win'):
        import msvcrt
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

        print(f"Est dans un coin : {self.is_corner(piece, x, y)}")
        print(f"Premire tour : {self.is_first_turn()}")
        print(f"Adjacent : {self.is_adjacent_to_same_color(piece,x,y)}")
        print(f"Diagonale : {self.check_diagonal_adjacency(x,y)}")

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

        if self.is_adjacent_to_same_color(piece, x, y) and not self.is_first_turn():
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
                        print("Coin trouvé!")  # Confirmation de la détection du coin
                        return True
        print("Aucun coin détecté pour cette pièce.")  # Indique qu'aucun coin n'a été détecté
        return False

    def is_adjacent_to_same_color(self, piece, x, y):
        """Vérifie si chaque coin de la pièce est correctement adjacente par les coins à une pièce de même couleur."""
        for i in range(len(piece)):
            for j in range(len(piece[i])):
                if piece[i][j] == "#":
                    if not self.check_diagonal_adjacency(x + i, y + j):
                        return False
        return True

    def check_diagonal_adjacency(self, x, y):
        """Vérifie si la case (x, y) est adjacente par les coins à une pièce de la même couleur."""
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]  # Diagonales
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < len(self.board) and 0 <= ny < len(self.board[0]):
                if self.board[nx][ny].startswith(self.player_colors[self.current_player]):
                    return True
        return False
       
    ### Principal code du jeu

    def show_menu(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("********** Menu **********")
        print("1. Commencer à jouer")
        print("2. Quitter")
        try:
            return int(input("Entrez votre choix : "))
        except ValueError:
            return 0  # Retourner une valeur non valide en cas d'erreur
    
    def initialize_game(self):
        """
        Initialisation du jeu. Cette méthode prépare le plateau de jeu, sélectionne les pièces,
        et définit le nombre de joueurs.
        """
        os.system("cls" if os.name == 'nt' else 'clear')

        # Création du plateau de jeu, sélection des pièces, etc.
        self.tab = self.crea_tab()  # Supposons que vous avez une méthode crea_tab pour initialiser le tableau
        self.current_piece_key = self.choose_piece()  # Méthode pour choisir la première pièce
        self.rotation_idx = 0  # Index de la rotation actuelle pour la pièce choisie
        self.x, self.y = 1, 1  # Positions initiales sur le plateau

        # Déterminer le nombre de joueurs
        print(f"Nombre de joueurs par défaut : {self.number_of_players}")
        change = input("Voulez-vous changer le nombre de joueurs ? (y/n): ").lower()
        if change == 'y':
            while True:
                try:
                    number = int(input("Entrez le nombre de joueurs (2-4): "))
                    if 2 <= number <= 4:
                        self.number_of_players = number
                        break
                    else:
                        print("S'il vous plaît, entrez un nombre valide de joueurs (2-4).")
                except ValueError:
                    print("Entrée invalide. Veuillez entrer un nombre.")
    
    def main(self):
        """
        Méthode pour démarrer le jeu. Elle gère la boucle principale du jeu,
        les actions des joueurs, et les mises à jour du plateau.
        """
        # Afficher le menu et obtenir le choix de l'utilisateur
        choice = self.show_menu()
        if choice == 2:
            return  # Quitter si l'utilisateur choisit cette option

        self.initialize_game()

        # Boucle principale du jeu
        while True:
            # Afficher le plateau avec la pièce actuelle
            self.display_board(self.blokus_pieces[self.current_piece_key][self.rotation_idx], self.x, self.y)
            
            # Instructions pour le joueur actuel
            print(f"Tour du joueur {self.current_player}. Utilisez z, q, s, d pour déplacer la pièce, 'a' pour la tourner à gauche, 'e' pour la tourner à droite, 'ENTRÉE' pour la placer. Appuyez sur 'k' pour quitter.")
            key_pressed = self.get_key()  # Lecture de l'entrée du clavier

            if key_pressed == 'k':  # Condition pour quitter le jeu
                print("Fin du jeu...")
                break

            # Traitement de l'action de placement de la pièce
            if key_pressed in ('\r', '\n'):
                current_piece = self.blokus_pieces[self.current_piece_key][self.rotation_idx]
                current_x = self.x
                current_y = self.y

                # Vérifier si la pièce peut être placée à cet endroit
                if self.can_place_piece(current_piece, current_x, current_y):
                    self.place_piece(current_piece, current_x, current_y)  # Placer la pièce

                    # Passer au joueur suivant (à ajuster selon votre logique de jeu)
                    self.current_player = (self.current_player % self.number_of_players) + 1

                    # Choisir la prochaine pièce pour le nouveau joueur actuel
                    self.current_piece_key = self.choose_piece()
                    self.rotation_idx = 0  # Réinitialiser la rotation pour la nouvelle pièce
                    self.x, self.y = 1, 1  # Réinitialiser les positions
                else:
                    print("Action impossible. Vous ne pouvez pas placer la pièce ici.")
            else:
                # Traitement des autres actions (déplacement, rotation)
                self.x, self.y, self.rotation_idx = self.modify_board(
                    self.current_piece_key, self.x, self.y, key_pressed, self.rotation_idx)

    def run(self):
        """
        Cette méthode gère le menu principal et les sélections d'options.
        """
        while True:
            user_choice = self.show_menu()
            if user_choice == 1:
                # Lancer le jeu
                self.main()
            elif user_choice == 2:
                print("Au revoir!")
                break
            else:
                print("Option invalide, veuillez réessayer.")
            
            input("Appuyez sur entrer pour continuer...")  # Pause avant de nettoyer l'écran
    
    
# Pour démarrer le jeu, vous créez une instance de votre jeu et appelez 'run'.
if __name__ == "__main__":
    game = BlukusGame()
    game.main()