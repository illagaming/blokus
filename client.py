import asyncio
import json
from game_logic import main_game  # Supposons que vous ayez un fichier séparé pour la logique du jeu.

async def tcp_echo_client():
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 8888)

    # Pour l'exemple, nous envoyons simplement une chaîne JSON.
    message = json.dumps({"action": "start_game"})
    writer.write(message.encode())
    await writer.drain()

    data = await reader.read(100)
    print(f'Received: {data.decode()}')

    print('Closing the connection')
    writer.close()
    await writer.wait_closed()

    # Commencez à jouer ici
    await main_game()  # Ceci est une fonction hypothétique, remplacez-la par votre fonction de démarrage de jeu réelle.

asyncio.run(tcp_echo_client())


# # Client
# # --------

# import asyncio 
# import json
# grille_tetris = [[0] * 10 for _ in range(20)]

# def placerPiece(posX,posY,pieces,grille):
#     bloc_L = [
#     [1, 0, 0],
#     [1, 1, 1]
#     ]
#     x, y = posX, posY
#     for i in range(len(bloc_L)):
#         for j in range(len(bloc_L[0])):
#             grille[y + i][x + j] = bloc_L[i][j]
#     return grille

# def afficheGrille () : 
#     for ligne in grille_tetris:
#         ligne_formattee = ["#" if cellule == 1 else "." for cellule in ligne]
#         print("".join(ligne_formattee))

# def convert(x):
#     if x=='A':return 10
#     elif x=='B':return 11
#     elif x=='C':return 12
#     elif x=='D':return 13
#     elif x=='E':return 14
#     elif x=='F':return 15
#     elif x=='G':return 16
#     elif x=='H':return 17
#     elif x=='I':return 18
#     elif x=='J':return 19
#     else : return int(x)
# s='*'
# piece='line'
# async def send_receive_matrix(reader, writer):
#     round=1
#     while True:
#         s=input("Appuyez sur la touche entrée ou 's' pour sortir... ")
#         if round==1:
#         # Modifier la matrice (ajout d'une valeur)
#             #matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
#             matrix = grille_tetris
#         else :
#             x=convert(s[0:1])
#             y=convert(s[2:3])
#             matrix=placerPiece(x,y,piece,matrix)
#             #matrix= matrix

#         matrix_json = json.dumps(matrix)
#         writer.write(matrix_json.encode())
#         print("Matrice envoyée au serveur")
#         for row in matrix:
#             print(row)
#         await writer.drain()

#         data = await reader.read(1024)
#         matrix_json = data.decode()
#         matrix = json.loads(matrix_json)
#         print("Matrice reçue du serveur :")
#         for row in matrix:
#             print(row)
#         round +=1
# async def main():
#     reader, writer = await asyncio.open_connection('127.0.0.1', 8888)

#     await send_receive_matrix(reader, writer)

#     writer.close()
#     await writer.wait_closed()

# asyncio.run(main())

