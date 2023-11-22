import random
import asyncio

class SimpleGame:
    def __init__(self):
        self.target_number = random.randint(1, 100)
        self.game_over = False

    async def guess_number(self, player_name, number):
        if self.game_over:
            return f"Game is already over!"

        print(f"{player_name} guesses {number}")
        if number < self.target_number:
            return "The number is higher!"
        elif number > self.target_number:
            return "The number is lower!"
        else:
            self.game_over = True
            return f"Congratulations, {player_name}! You have guessed the number."

    async def reset_game(self):
        self.target_number = random.randint(1, 100)
        self.game_over = False
        print("Game has been reset.")

# Cette fonction hypothétique représente la boucle de jeu principale, où la logique du jeu est gérée.
async def main_game():
    game = SimpleGame()
    
    player_name = "Player1"  # Ce serait dynamique dans un vrai jeu, peut-être déterminé par des entrées de l'utilisateur.
    
    # Supposons que le joueur continue à deviner avec des entrées simulées jusqu'à ce qu'il gagne.
    while not game.game_over:
        player_guess = random.randint(1, 100)  # Dans un vrai jeu, vous obtiendriez cela à partir de l'entrée du joueur.
        result = await game.guess_number(player_name, player_guess)
        print(result)

        await asyncio.sleep(1)  # Faire une pause pour simuler le temps de réflexion du joueur.

    await game.reset_game()  # Réinitialisez le jeu, prêt pour la prochaine partie.

# Pour tester directement ce fichier, sinon, il sera appelé par client.py
if __name__ == "__main__":
    asyncio.run(main_game())
