/**
 * Evolution API Configuration
 * 
 * Configuração para integração com Evolution API para envio de mensagens WhatsApp
 */

const EVOLUTION_CONFIG = {
    // URL base da Evolution API
    API_URL: 'https://chatbot-evolution-api.zv7gpn.easypanel.host',
    
    // API Key para autenticação
    API_KEY: '29683C4C977415CAAFCCE10F7D57E11',
    
    // Nome da instância
    INSTANCE_NAME: 'hakimfarma',
    
    // Número do vendedor (com código do país)
    SELLER_PHONE: '5512976021836',
    
    // Delay entre mensagens (ms)
    MESSAGE_DELAY: 1200,
    
    // Timeout para requisições (ms)
    REQUEST_TIMEOUT: 10000
};

/**
 * Envia mensagem de texto via Evolution API
 * 
 * @param {string} number - Número do destinatário (com código do país)
 * @param {string} text - Texto da mensagem
 * @param {number} delay - Delay antes de enviar (opcional)
 * @returns {Promise<Object>} Resposta da API
 */
async function sendTextMessage(number, text, delay = EVOLUTION_CONFIG.MESSAGE_DELAY) {
    const url = `${EVOLUTION_CONFIG.API_URL}/message/sendText/${EVOLUTION_CONFIG.INSTANCE_NAME}`;
    
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'apikey': EVOLUTION_CONFIG.API_KEY
            },
            body: JSON.stringify({
                number: number,
                text: text,
                delay: delay
            }),
            signal: AbortSignal.timeout(EVOLUTION_CONFIG.REQUEST_TIMEOUT)
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status} - ${JSON.stringify(result)}`);
        }
        
        return {
            success: true,
            data: result
        };
        
    } catch (error) {
        console.error('Erro ao enviar mensagem:', error);
        return {
            success: false,
            error: error.message
        };
    }
}

/**
 * Envia mensagem com mídia via Evolution API
 * 
 * @param {string} number - Número do destinatário
 * @param {string} mediaUrl - URL da mídia (imagem, vídeo, etc)
 * @param {string} caption - Legenda da mídia (opcional)
 * @returns {Promise<Object>} Resposta da API
 */
async function sendMediaMessage(number, mediaUrl, caption = '') {
    const url = `${EVOLUTION_CONFIG.API_URL}/message/sendMedia/${EVOLUTION_CONFIG.INSTANCE_NAME}`;
    
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'apikey': EVOLUTION_CONFIG.API_KEY
            },
            body: JSON.stringify({
                number: number,
                mediaUrl: mediaUrl,
                caption: caption,
                delay: EVOLUTION_CONFIG.MESSAGE_DELAY
            }),
            signal: AbortSignal.timeout(EVOLUTION_CONFIG.REQUEST_TIMEOUT)
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status} - ${JSON.stringify(result)}`);
        }
        
        return {
            success: true,
            data: result
        };
        
    } catch (error) {
        console.error('Erro ao enviar mídia:', error);
        return {
            success: false,
            error: error.message
        };
    }
}

/**
 * Verifica status da instância
 * 
 * @returns {Promise<Object>} Status da instância
 */
async function checkInstanceStatus() {
    const url = `${EVOLUTION_CONFIG.API_URL}/instance/connectionState/${EVOLUTION_CONFIG.INSTANCE_NAME}`;
    
    try {
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'apikey': EVOLUTION_CONFIG.API_KEY
            }
        });
        
        const result = await response.json();
        
        return {
            success: response.ok,
            data: result
        };
        
    } catch (error) {
        console.error('Erro ao verificar status:', error);
        return {
            success: false,
            error: error.message
        };
    }
}

// Exportar configuração e funções
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        EVOLUTION_CONFIG,
        sendTextMessage,
        sendMediaMessage,
        checkInstanceStatus
    };
}
