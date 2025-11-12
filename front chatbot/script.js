// script.js (versão final)
document.addEventListener('DOMContentLoaded', function() {
    // --- ELEMENTOS DA NAVEGAÇÃO ---
    const floatButton = document.getElementById('float-button');
    const mainWindow = document.getElementById('main-window');
    const welcomeScreen = document.getElementById('welcome-screen');
    const chatScreen = document.getElementById('chat-screen');
    const startChatButton = document.getElementById('start-chat-button');
    const backButtons = document.querySelectorAll('.back-button');

    // --- ELEMENTOS DO CHAT ---
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const messagesArea = document.getElementById('messages-area');
    const apiUrl = 'http://127.0.0.1:8000/chat/';

    // --- LÓGICA DE NAVEGAÇÃO ENTRE TELAS (Seu código original) ---
    floatButton.addEventListener('click', () => {
        mainWindow.classList.add('visible');
        floatButton.style.display = 'none';
    });

    function closeChat() {
        mainWindow.classList.remove('visible');
        floatButton.style.display = 'flex';
        welcomeScreen.classList.remove('hidden');
        chatScreen.classList.add('hidden');
    }

    backButtons.forEach(button => {
        button.addEventListener('click', () => {
            if (!chatScreen.classList.contains('hidden')) {
                chatScreen.classList.add('hidden');
                welcomeScreen.classList.remove('hidden');
            } else {
                closeChat();
            }
        });
    });

    startChatButton.addEventListener('click', () => {
        welcomeScreen.classList.add('hidden');
        chatScreen.classList.remove('hidden');
    });

    // --- NOVA LÓGICA DE COMUNICAÇÃO COM A API ---

    chatForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Previne que a página recarregue
        
        const pergunta = chatInput.value.trim();
        if (!pergunta) return;

        // 1. Mostra a mensagem do usuário na tela
        addMessage(pergunta, 'user');
        chatInput.value = ''; // Limpa o campo

        try {
            // 2. Mostra um indicador de "digitando"
            addMessage('Digitando...', 'bot-loading');

            // 3. Envia a pergunta para a API
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ texto: pergunta })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            // 4. Remove o "digitando" e mostra a resposta do bot
            removeLoadingMessage();
            addMessage(data.resposta, 'bot');

        } catch (error) {
            console.error('Falha ao comunicar com a API:', error);
            removeLoadingMessage();
            addMessage('Desculpe, estou com problemas de conexão. Tente novamente.', 'bot');
        }
    });

// Função para adicionar uma nova mensagem na tela (ATUALIZADA)
    function addMessage(text, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;

    // --- Início da Atualização ---

    // 1. Converte a formatação Markdown para HTML
    // Primeiro, converte **negrito** para <strong>...</strong>
    let htmlText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Depois, converte *itálico* (opcional) para <em>...</em>
    // Importante: Isso deve vir DEPOIS do negrito, para não confundir
    htmlText = htmlText.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // 2. Define o conteúdo da div como HTML, em vez de texto puro
    // Isso faz o navegador "ler" as tags <strong> e renderizar o negrito
    messageDiv.innerHTML = htmlText;

    // --- Fim da Atualização ---

    messagesArea.appendChild(messageDiv);
    // Rola a conversa para a última mensagem
    messagesArea.scrollTop = messagesArea.scrollHeight;
}
    
    // Função para remover o indicador "Digitando..."
    function removeLoadingMessage() {
        const loadingMessage = document.querySelector('.bot-loading');
        if (loadingMessage) {
            loadingMessage.remove();
        }
    }
});