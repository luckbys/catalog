// Script de diagnóstico para problemas de imagens
console.log('🔍 Iniciando diagnóstico de imagens...');

const API_BASE = 'http://localhost:8000';

// Função para testar se uma URL de imagem carrega
async function testImageUrl(url, name) {
    return new Promise((resolve) => {
        const img = new Image();
        const startTime = Date.now();
        
        img.onload = () => {
            const loadTime = Date.now() - startTime;
            console.log(`✅ ${name}: OK (${loadTime}ms)`);
            console.log(`   URL: ${url}`);
            resolve({ success: true, url, name, loadTime });
        };
        
        img.onerror = (error) => {
            console.error(`❌ ${name}: FALHOU`);
            console.error(`   URL: ${url}`);
            console.error(`   Erro:`, error);
            resolve({ success: false, url, name, error });
        };
        
        img.src = url;
        
        // Timeout de 10 segundos
        setTimeout(() => {
            if (!img.complete) {
                console.warn(`⏱️ ${name}: TIMEOUT (>10s)`);
                resolve({ success: false, url, name, error: 'timeout' });
            }
        }, 10000);
    });
}

// Função para testar produtos da API
async function testAPIProducts(sessionId) {
    console.log('\n📡 Testando produtos da API...');
    console.log(`   Session ID: ${sessionId || 'não fornecido'}`);
    
    if (!sessionId) {
        console.warn('⚠️ Sem sessao_id. Use: ?sessao_id=XXX');
        return [];
    }
    
    try {
        const url = `${API_BASE}/api/produtos/${sessionId}`;
        console.log(`   Fazendo fetch: ${url}`);
        
        const res = await fetch(url);
        console.log(`   Status: ${res.status} ${res.statusText}`);
        
        if (!res.ok) {
            console.error('❌ Resposta não OK');
            return [];
        }
        
        const data = await res.json();
        console.log(`   Produtos recebidos: ${data.produtos?.length || 0}`);
        
        if (data.produtos && data.produtos.length > 0) {
            console.log('\n🖼️ Testando imagens dos produtos da API...');
            
            for (const produto of data.produtos.slice(0, 5)) {
                const imageUrl = produto.imagem_url || './public/padrao.png';
                await testImageUrl(imageUrl, produto.descricao);
            }
        }
        
        return data.produtos || [];
    } catch (error) {
        console.error('❌ Erro ao buscar produtos:', error);
        return [];
    }
}

// Função principal de diagnóstico
async function runDiagnostics() {
    console.log('\n=== DIAGNÓSTICO DE IMAGENS ===\n');
    
    // 1. Testar imagens locais
    console.log('1️⃣ Testando imagens locais...\n');
    await testImageUrl('./public/padrao.png', 'Imagem Padrão (relativa)');
    await testImageUrl('/public/padrao.png', 'Imagem Padrão (absoluta)');
    await testImageUrl(`${API_BASE}/public/padrao.png`, 'Imagem Padrão (via API)');
    await testImageUrl('./public/logo.png', 'Logo (relativa)');
    
    // 2. Testar imagens externas
    console.log('\n2️⃣ Testando imagens externas...\n');
    await testImageUrl('https://placehold.co/300x300/e0f2fe/0284c7?text=Teste', 'Placeholder');
    await testImageUrl('https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400', 'Unsplash');
    
    // 3. Testar produtos da API
    console.log('\n3️⃣ Testando produtos da API...\n');
    const params = new URLSearchParams(window.location.search);
    const sessionId = params.get('sessao_id');
    await testAPIProducts(sessionId);
    
    // 4. Verificar configuração do navegador
    console.log('\n4️⃣ Verificando configuração do navegador...\n');
    console.log(`   User Agent: ${navigator.userAgent}`);
    console.log(`   Online: ${navigator.onLine}`);
    console.log(`   Cookies habilitados: ${navigator.cookieEnabled}`);
    
    // 5. Verificar localStorage
    console.log('\n5️⃣ Verificando localStorage...\n');
    try {
        const cart = localStorage.getItem('cart');
        console.log(`   Carrinho: ${cart ? 'existe' : 'vazio'}`);
        if (cart) {
            const parsed = JSON.parse(cart);
            console.log(`   Itens no carrinho: ${Object.keys(parsed).length}`);
        }
    } catch (e) {
        console.error('   Erro ao acessar localStorage:', e);
    }
    
    console.log('\n=== FIM DO DIAGNÓSTICO ===\n');
    console.log('💡 Dica: Abra o Network tab do DevTools para ver detalhes das requisições');
}

// Executar diagnóstico quando a página carregar
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', runDiagnostics);
} else {
    runDiagnostics();
}

// Exportar para uso no console
window.runImageDiagnostics = runDiagnostics;
window.testImageUrl = testImageUrl;

console.log('💡 Você pode executar novamente com: runImageDiagnostics()');
