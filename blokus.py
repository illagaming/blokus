import os
try:
    import getch as msvcrt   # Linux
except ImportError:
    import msvcrt         # Windows

class BlukusGame:
    def __init__(self):
        self.board = [[' ' for _ in range(20)] for _ in range(20)]  # Un plateau de jeu 20x20
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
        self.blokus_pieces = self.pieces()
        self.player_colors = {
            1: '\033[92m',  # Vert
            2: '\033[91m',  # Rouge
            3: '\033[34m',  # Bleu
            4: '\033[93m'   # Jaune
        }
        self.rotation_idx = 0
        self.x, self.y = 1, 1
        self.number_of_players = 4

    # Récupère la touche pressée par l'utilisateur
    def get_key():
        return msvcrt.getch().decode('utf-8', errors="ignore")

# Fait pivoter la pièce de 90 degrés
def rotate(piece):
    transposed = [list(row) for row in zip(*piece)]
    return [row[::-1] for row in transposed]

# Génère toutes les rotations possibles pour une pièce donnée
def generate_rotations(piece):
    rotations = [piece]
    for _ in range(3):
        rotations.append(rotate(rotations[-1]))
    return rotations

# Définit les pièces Blokus et génère leurs rotations
def pieces():
    blokus_pieces = {
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
    
    # Génère toutes les rotations pour chaque pièce
    for key, piece in blokus_pieces.items():
        blokus_pieces[key] = generate_rotations(piece)
    
    return blokus_pieces

blokus_pieces = pieces()

# Choisir la pièce à utiliser
def choose_piece(blokus_pieces): 
    os.system('cls')
    print("Pièces disponibles :")
    for index, piece in enumerate(blokus_pieces, 1):
        print(f"{index}: {piece}")

    while True:
        try:
            choice = int(input("Entrez le numéro de la pièce que vous souhaitez utiliser : "))
            if 1 <= choice <= len(blokus_pieces):
                return list(blokus_pieces.keys())[choice - 1]  # Retourne la clé de la pièce choisie
            else:
                print("Sélection non valide. Veuillez choisir un numéro de la liste.")
        except ValueError:
            print("Veuillez entrer un nombre.")

# Crée le plateau de jeu initial
def crea_tab():
    tab = [['*'] * 22 for _ in range(22)]
    for i in range(1, 21):
        for y in range(1, 21):
            tab[i][y] = ' '    
    return tab

# Affiche le plateau de jeu actuel avec la pièce en mouvement
def display_tab(tab, piece, x, y, color_code):
    os.system("cls")
    display_tab = [row.copy() for row in tab]
    for i in range(len(piece)):
        for j in range(len(piece[i])):
            if piece[i][j] == "#":
                display_tab[i + x][j + y] = color_code + '#\033[0m'
    for row in display_tab:
        print(' '.join(row))

# Vérifie si la pièce peut être placée à une position donnée
def can_place_piece(tab, piece, x, y):
    for i in range(len(piece)):
        for j in range(len(piece[i])):
            if piece[i][j] == "#":
                if tab[i + x][j + y] != ' ':
                    return False
    return True

# Vérifie si la pièce peut se déplacer vers une position donnée
def can_move_to(tab, piece, x, y):
    for i in range(len(piece)):
        for j in range(len(piece[i])):
            if piece[i][j] == "#":
                if i + x < 0 or i + x >= len(tab) or j + y < 0 or j + y >= len(tab[0]):
                    return False
    return True

# Modifie la position ou l'orientation de la pièce selon la touche pressée
def modif_tab(current_piece_key, tab, x, y, key_pressed, piece, rotation_idx):
    if key_pressed == 'z':
        if can_move_to(tab, piece, x - 1, y):
            x -= 1
    elif key_pressed == 's':
        if can_move_to(tab, piece, x + 1, y):
            x += 1
    elif key_pressed == 'q':
        if can_move_to(tab, piece, x, y - 1):
            y -= 1
    elif key_pressed == 'd':
        if can_move_to(tab, piece, x, y + 1):
            y += 1
    elif key_pressed == 'a':
        rotation_idx = (rotation_idx - 1) % 4
        if not can_move_to(tab, blokus_pieces[current_piece_key][rotation_idx], x, y):
            rotation_idx = (rotation_idx + 1) % 4
    elif key_pressed == 'e':
        rotation_idx = (rotation_idx + 1) % 4
        if not can_move_to(tab, blokus_pieces[current_piece_key][rotation_idx], x, y):
            rotation_idx = (rotation_idx - 1) % 4

    return x, y, rotation_idx
   
    
### Principal code du jeu

def show_menu():
    os.system('cls')
    print("********** Menu **********")
    print("1. Commencer à jouer")
    print("2. Quitter")
    try:
        return int(input("Entrez votre choix : "))
    except ValueError:
        return 0  # retourner une valeur non valide en cas d'erreur

#print(choose_piece(blokus_pieces))
    
def main(): 
    os.system("cls")

    # Initialisation des variables
    current_player = 1
    current_piece_key = choose_piece(blokus_pieces)
    player_colors = {
        1: '\033[92m',  # Vert
        2: '\033[91m',  # Rouge
        3: '\033[34m',  # Bleu
        4: '\033[93m'   # Jaune
    }
    rotation_idx = 0
    x, y = 1, 1
    tab = crea_tab()

    # Determiner le nombre de joueurs
    number_of_players = 4 
    
    # Option pour changer le nombre de joueurs
    print(f"Nombre de joueurs par défaut : {number_of_players}")
    change = input("Voulez-vous changer le nombre de joueurs ? (y/n): ").lower()
    if change == 'y':
        while True:
            try:
                number_of_players = int(input("Entrez le nombre de joueurs (2-4): "))
                if 2 <= number_of_players <= 4:
                    break
                else:
                    print("S'il vous plaît, entrez un nombre valide de joueurs (2-4).")
            except ValueError:
                print("Entrée invalide. Veuillez entrer un nombre.")

    display_tab(tab, blokus_pieces[current_piece_key][rotation_idx], x, y, player_colors[current_player])  # Affiche le plateau au démarrage

    ### Boucle principale du jeu
    while True:
        print(f"Joueur {current_player}: Utilisez z, q, s, d pour déplacer le #. Appuyez sur 'a' pour tourner à gauche et 'e' pour tourner à droite. Appuyez sur 'ENTRER' pour placer la pièce. Appuyez sur 'k' pour quitter.")
        key_pressed = get_key()
        
        if key_pressed == 'k': 
            os.system("cls")
            break
            
        if key_pressed == '\r':
            if can_place_piece(tab, blokus_pieces[current_piece_key][rotation_idx], x, y):
                for i in range(len(blokus_pieces[current_piece_key][rotation_idx])):
                    for j in range(len(blokus_pieces[current_piece_key][rotation_idx][i])):
                        if blokus_pieces[current_piece_key][rotation_idx][i][j] == "#":
                            tab[i + x][j + y] = player_colors[current_player] + "#" + '\033[0m'  # Utiliser la couleur du joueur actuel

                # Passez au prochain joueur
                current_player += 1
                if current_player > number_of_players:
                    current_player = 1  # Retour au premier joueur après le dernier

                x, y = 1, 1  # Réinitialisez la position pour le prochain joueur
                current_piece_key = choose_piece(blokus_pieces)  # Choisir une nouvelle pièce

        x, y, rotation_idx = modif_tab(current_piece_key, tab, x, y, key_pressed, blokus_pieces[current_piece_key][rotation_idx], rotation_idx)
        # Actualise l'affichage après chaque mouvement ou placement de pièce
        display_tab(tab, blokus_pieces[current_piece_key][rotation_idx], x, y, player_colors[current_player])

while True :
    user_choice = show_menu()
    if user_choice == 1:
        # Lancer le jeu
        main()
    elif user_choice == 2:
        print("Au revoir")
        break
    else:
        print("Option invalide, veuillez reesayer")
    print("Appuyez sur entrer pour continuer...") 
    
# Limiter le nombre de pièces
# Contraintes pour poser les pièces 