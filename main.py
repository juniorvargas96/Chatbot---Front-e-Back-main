# main.py
from utils import limpar_tela, mostrar_cabecalho
from scraper import carregar_contexto
from chat_manager import iniciar_chat
from config.settings import settings
import logging
from logging_config import configurar_logging
from sentence_transformers import util
import requests

util.http_get = lambda *args, **kwargs: requests.get(*args, **kwargs, stream=False)


def main():
    configurar_logging()
    logging.info("Iniciando aplicação")
    
    try:
        limpar_tela()
        print("Iniciando o NPC Chatbot...")
        
        contexto = carregar_contexto(settings.URLS_PARA_SCRAPING, settings.USE_CACHE)
        if not contexto:
            raise RuntimeError("Não foi possível carregar o contexto necessário")
            
        mostrar_cabecalho()
        iniciar_chat(contexto)

    
    except Exception as e:
        logging.critical(f"Erro fatal: {str(e)}")
        print(f"\n🚨 Ocorreu um erro crítico: {str(e)}")
        print("Por favor, tente novamente mais tarde.")

    finally:
        logging.info("Aplicação finalizada.")

if __name__ == "__main__":
    main()