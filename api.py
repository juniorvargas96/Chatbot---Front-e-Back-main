# api.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from scraper import carregar_contexto
from chat_manager import iniciar_chat_api
from config.settings import settings
from logging_config import configurar_logging

import logging

logger = logging.getLogger(__name__)

# Variável global para manter o contexto carregado sob demanda
contexto_global = None

# -------------------- Lifespan (Startup & Shutdown) -------------------- #

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        configurar_logging()
        logger.info("🚀 Iniciando API (carregamento de contexto será sob demanda).")
        yield  # API ativa aqui
    finally:
        logger.info("🔒 Encerrando aplicação e fechando cache...")
        cache_manager.close()
        logger.info("✅ Cache fechado com sucesso.")

# ------------------------- Inicialização FastAPI ------------------------ #

app = FastAPI(
    title="NPC Chatbot API",
    description="API do assistente NPC para responder dúvidas sobre o Programa Jovem Programador.",
    version="1.0.0",
    lifespan=lifespan
)

origins = ["*"]  # Permite todas as origens (ideal para dev)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------- Carregamento sob demanda ----------------------- #

async def get_contexto():
    """
    Carrega o contexto somente quando necessário.
    Evita estouro de memória no Render durante o deploy.
    """
    global contexto_global
    if contexto_global is None:
        logger.info("⏳ Carregando contexto sob demanda...")
        contexto_global = carregar_contexto(settings.URLS_PARA_SCRAPING, settings.USE_CACHE)
        logger.info("✅ Contexto carregado sob demanda.")
    return contexto_global

# ----------------------------- Models ----------------------------- #

class Mensagem(BaseModel):
    texto: str

# ---------------------------- Rotas ----------------------------- #

@app.post("/chat/", summary="Enviar pergunta ao NPC")
async def chat(mensagem: Mensagem):
    try:
        contexto = await get_contexto()
        resposta = iniciar_chat_api(mensagem.texto, contexto)
        return {"resposta": resposta}
    except Exception as e:
        logger.exception("Erro ao processar pergunta")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@app.get("/cache/stats", summary="Ver estatísticas do cache")
def stats():
    return cache_manager.get_cache_stats()
