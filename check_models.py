import os
import google.generativeai as genai
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

try:
    # Pega a chave de API do ambiente
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY não encontrada no arquivo .env!")

    genai.configure(api_key=api_key)

    print("✅ Chave de API configurada. Listando modelos disponíveis...")
    print("-" * 50)

    model_found = False
    # Itera sobre todos os modelos que sua chave pode acessar
    for model in genai.list_models():
        # Verifica se o modelo suporta o método 'generateContent' que o chatbot usa
        if 'generateContent' in model.supported_generation_methods:
            print(f"-> Nome do Modelo: {model.name}")
            model_found = True
    
    if not model_found:
        print("\n❌ Nenhum modelo compatível com 'generateContent' foi encontrado para sua chave.")
        print("Isso pode ser um problema de permissão na sua conta Google Cloud ou a API pode não estar habilitada corretamente.")

    print("-" * 50)

except Exception as e:
    print(f"\n🚨 Ocorreu um erro ao tentar conectar com a API do Google: {e}")
    print("\nVerifique os seguintes pontos:")
    print("1. O arquivo .env está na mesma pasta que este script?")
    print("2. A chave GOOGLE_API_KEY está correta no arquivo .env?")
    print("3. Você tem conexão com a internet?")
    print("4. A API 'Generative Language' está ativada no seu projeto Google Cloud?")