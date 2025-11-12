import requests
from bs4 import BeautifulSoup
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

def buscar_conteudo_da_url(url: str) -> str | None:
    headers = {'User-Agent': settings.USER_AGENT}
    try:
        response = requests.get(url, headers=headers, timeout=settings.TIMEOUT_REQUISICAO)
        response.raise_for_status()
        
        # Verificar tipo de conteúdo
        content_type = response.headers.get('Content-Type', '')
        if 'text/html' not in content_type:
            raise ValueError(f"Conteúdo não HTML: {content_type}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remover elementos indesejados
        for tag in soup(['script', 'style', 'header', 'footer', 'nav', 'aside', 'form']):
            tag.decompose()
        
        # Tentar encontrar conteúdo principal
        main_content = soup.find('main') or soup.find('article') or soup.body
        
        if not main_content:
            raise ValueError("Nenhum conteúdo principal encontrado")
        
        return main_content.get_text(separator='\n', strip=True)
        
    except Exception as e:
        logger.error(f"Erro ao processar {url}: {str(e)}")
        return None

def carregar_contexto(urls, use_cache=False):
    if use_cache and os.path.exists(settings.CACHE_FILE):
        try:
            with open(settings.CACHE_FILE, 'r', encoding='utf-8') as f:
                logger.info("Usando conteúdo em cache")
                return f.read()
        except Exception as e:
            logger.warning(f"Erro ao ler cache: {str(e)}")
    
    logger.info("Buscando informações atualizadas do site...")
    textos_combinados = []
    
    for url in urls:
        texto = buscar_conteudo_da_url(url)
        if texto:
            textos_combinados.append(texto)
    
    if not textos_combinados:
        raise RuntimeError("Não foi possível carregar nenhuma informação dos sites.")
    
    contexto = "\n\n--- FIM DA PÁGINA ---\n\n".join(textos_combinados)
    
    if use_cache:
        try:
            with open(settings.CACHE_FILE, 'w', encoding='utf-8') as f:
                f.write(contexto)
        except Exception as e:
            logger.error(f"Erro ao salvar cache: {str(e)}")
    
    return contexto