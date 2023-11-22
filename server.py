import asyncio
import json

async def handle_client(reader, writer):
    data = await reader.read(100)
    message = json.loads(data.decode())
    
    # Gérer les différentes actions du jeu ici, telles que la mise à jour du jeu, etc.
    # Pour cet exemple, nous renvoyons simplement le message au client.
    
    print(f"Received {message} from client")
    print("Sending back to client")
    
    new_message = json.dumps({"response": "Received your message!"})
    writer.write(new_message.encode())
    await writer.drain()

    writer.close()

async def main():
    server = await asyncio.start_server(
        handle_client, '127.0.0.1', 8888)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()

asyncio.run(main())



# # Serveur
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
# async def handle_client(reader, writer):
#     round=1
#     while True:
#         data = await reader.read(1024)
#         if not data:
#             break
#         matrix_json = data.decode()
#         matrix = json.loads(matrix_json)
#         print("Matrice reçue du client :")
#         for row in matrix:
#             print(row)
#         s=input("Appuyez sur la touche entrée ou 's' pour sortir... ")
#         # Modifier la matrice (ajout d'une valeur)
#         x=convert(s[0:1])
#         y=convert(s[2:3])
#         matrix=placerPiece(x,y,piece,matrix)
#         #matrix[1][1] +=round
#         matrix_json = json.dumps(matrix)
#         writer.write(matrix_json.encode())
#         await writer.drain()
#         print("Matrice modifiée renvoyée au client")
#         for row in matrix:
#             print(row)
#         round +=1
#     writer.close()

# async def main():
#     server = await asyncio.start_server(
#         handle_client, '127.0.0.1', 8888)

#     addr = server.sockets[0].getsockname()
#     print(f'Serveur en attente de connexions sur {addr}')

#     async with server:
#         await server.serve_forever()

# asyncio.run(main())