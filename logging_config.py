import logging
import os

def configurar_logging():
    #configuração principal
    logging.basicConfig(
        level=logging.WARNING,
        format='%(asctime)s - %(name)s - %(message)s',
        handlers=[
            logging.FileHandler("chatbot.log") #apenas arquivo
            #remova o streamHandler() para não mostar no terminal
        ]


    )
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    log_level = logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.FileHandler("chatbot.log"),
            logging.StreamHandler()
        ]
    )
    
    # Reduzir verbosidade de algumas bibliotecas
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)