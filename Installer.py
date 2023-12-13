import subprocess
import sys
if sys.platform.startswith('linux') or sys.platform.startswith('ubuntu') :
    commande = "sudo apt-get update && sudo apt-get install websockets && sudo apt-get install readchar"
    try:
        # Exécute la commande apt-get pour installer websockets
        resultat = subprocess.run(commande, shell=True, capture_output=True, check=True, text=True)
        print(resultat.stdout)
        print('')
        print("Les bibliothèques ont été installées avec succès.")
    except subprocess.CalledProcessError as e:
        print("Erreur lors de l'installation des bibliothèques, veuillez essayer manuellement:")
        print("-websockets")
        print("-readchar")
        print('')
        print("Detailles:",e)
        sys.exit(1)
elif sys.platform.startswith('win'):
    commande = "pip install websockets"
    try:
        resultat = subprocess.run(commande, shell=True, capture_output=True, check=True, text=True)
        print(resultat.stdout)
        print('')
        print("Les bibliothèques ont été installées avec succès.")
    except subprocess.CalledProcessError as e:
        print("Erreur lors de l'installation des bibliothèques, veuillez essayer manuellement:")
        print("-websockets")
        print('')
        print("Detailles:",e)
else:
    raise OSError("Ce script ne supporte que Windows et Linux.")