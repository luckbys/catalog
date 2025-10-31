const fs = require('fs');

try {
    // Ler o arquivo HTML
    const html = fs.readFileSync('catalogo.html', 'utf8');
    
    // Extrair conteúdo entre tags <script>
    const scriptMatches = html.match(/<script[^>]*>([\s\S]*?)<\/script>/gi);
    
    if (scriptMatches) {
        scriptMatches.forEach((script, index) => {
            // Remover as tags <script>
            const jsContent = script.replace(/<script[^>]*>|<\/script>/gi, '');
            
            console.log(`\n=== SCRIPT ${index + 1} ===`);
            
            try {
                // Tentar fazer parse do JavaScript
                new Function(jsContent);
                console.log('✅ Sintaxe válida');
            } catch (error) {
                console.log('❌ Erro de sintaxe:', error.message);
                
                // Mostrar as linhas ao redor do erro
                const lines = jsContent.split('\n');
                const errorLine = error.message.match(/line (\d+)/);
                if (errorLine) {
                    const lineNum = parseInt(errorLine[1]);
                    const start = Math.max(0, lineNum - 3);
                    const end = Math.min(lines.length, lineNum + 2);
                    
                    console.log('\nLinhas ao redor do erro:');
                    for (let i = start; i < end; i++) {
                        const marker = i === lineNum - 1 ? '>>> ' : '    ';
                        console.log(`${marker}${i + 1}: ${lines[i]}`);
                    }
                }
            }
        });
    } else {
        console.log('Nenhum script encontrado');
    }
} catch (error) {
    console.error('Erro ao ler arquivo:', error.message);
}