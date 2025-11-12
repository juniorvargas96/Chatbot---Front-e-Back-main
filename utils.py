import os

class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def mostrar_cabecalho():
    limpar_tela()
    print(f"{Colors.BLUE}--- Chatbot Jovem Programador (Versão Terminal) ---{Colors.RESET}")
    print("Digite 'sair' a qualquer momento para terminar a conversa.")
    print("-" * 50)