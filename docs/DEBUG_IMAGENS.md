# 🔍 Guia de Diagnóstico de Imagens Quebradas

## Problema
As imagens dos produtos no catálogo não estão aparecendo (imagens quebradas).

## Correções Aplicadas

### 1. Correção no `catalogo.html`
- ✅ Corrigido caminho da imagem padrão de `/public/padrao.png` para `./public/padrao.png`
- ✅ Adicionada função `handleImageError()` com múltiplos fallbacks
- ✅ Adicionados logs de debug para rastrear URLs das imagens
- ✅ Removida duplicação do atributo `onerror`

### 2. Ferramentas de Diagnóstico Criadas

#### `test-product-images.html`
Interface visual completa para testar o carregamento de imagens dos produtos.

**Como usar:**
```bash
# Abrir no navegador com session ID
http://localhost:8000/test-product-images.html?sessao_id=SEU_SESSION_ID
```

**Recursos:**
- ✅ Visualização em grid dos produtos
- ✅ Status de carregamento em tempo real
- ✅ Estatísticas (total, sucesso, erro, tempo médio)
- ✅ Exibição da URL de cada imagem
- ✅ Fallback automático para imagem padrão

#### `test-images.html`
Teste simples de diferentes caminhos de imagem.

**Como usar:**
```bash
http://localhost:8000/test-images.html?sessao_id=SEU_SESSION_ID
```

**Testa:**
- Imagem padrão (relativa, absoluta, via API)
- Placeholders externos
- Imagens do Unsplash
- Produtos da API

#### `diagnose-images.js`
Script de diagnóstico para executar no console do navegador.

**Como usar:**
1. Abra o catálogo no navegador
2. Abra o DevTools (F12)
3. Vá para a aba Console
4. O script já estará carregado e executado automaticamente
5. Para executar novamente: `runImageDiagnostics()`

## Como Diagnosticar o Problema

### Passo 1: Verificar se o backend está rodando
```bash
# Verificar se o backend está acessível
curl http://localhost:8000/public/padrao.png
```

Se retornar erro, o backend não está servindo os arquivos estáticos corretamente.

### Passo 2: Testar com a página de diagnóstico
```bash
# Abrir no navegador
http://localhost:8000/test-product-images.html?sessao_id=SEU_SESSION_ID
```

Observe:
- ✅ Quantas imagens carregaram com sucesso
- ❌ Quantas falharam
- 🔗 As URLs que estão sendo usadas

### Passo 3: Verificar o console do navegador
1. Abra o catálogo: `http://localhost:8000/catalogo.html?sessao_id=SEU_SESSION_ID`
2. Abra o DevTools (F12)
3. Vá para a aba Console
4. Procure por mensagens como:
   - `[DEBUG] Produto: ... | imagem_url: ... | URL final: ...`
   - `⚠️ Falha ao carregar imagem para: ...`

### Passo 4: Verificar a aba Network
1. No DevTools, vá para a aba Network
2. Filtre por "Img"
3. Recarregue a página
4. Observe:
   - Status das requisições (200 = OK, 404 = não encontrado, etc.)
   - URLs completas das imagens
   - Tempo de carregamento

## Possíveis Causas e Soluções

### Causa 1: URLs das imagens estão incorretas no banco de dados
**Sintoma:** Todas as imagens falham, mesmo a padrão funciona

**Solução:**
```sql
-- Verificar as URLs no banco
SELECT id, descricao, imagem_url FROM produtos_sessao LIMIT 5;

-- Se necessário, atualizar para usar imagens válidas
UPDATE produtos_sessao SET imagem_url = 'https://placehold.co/300x300/e0f2fe/0284c7?text=Produto' WHERE imagem_url IS NULL OR imagem_url = '';
```

### Causa 2: Problema de CORS com imagens externas
**Sintoma:** Imagens do Unsplash ou outros domínios externos não carregam

**Solução:** As imagens externas devem funcionar, mas se houver problema de CORS, use imagens locais ou do mesmo domínio.

### Causa 3: Caminho da imagem padrão incorreto
**Sintoma:** Quando uma imagem falha, o fallback também não funciona

**Solução:** Já corrigido! A função `handleImageError()` tenta múltiplos caminhos:
- `./public/padrao.png`
- `/public/padrao.png`
- `http://localhost:8000/public/padrao.png`

### Causa 4: Backend não está servindo arquivos estáticos
**Sintoma:** Nenhuma imagem local carrega

**Solução:**
```bash
# Verificar se o diretório public existe
ls -la public/

# Verificar se padrao.png existe
ls -la public/padrao.png

# Reiniciar o backend
cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## Logs de Debug Adicionados

O catálogo agora exibe logs detalhados no console:

```javascript
// Ao carregar produtos da API
[DEBUG] Produto: Nome do Produto | imagem_url: URL_ORIGINAL | URL final: URL_USADA

// Ao falhar o carregamento
⚠️ Falha ao carregar imagem para: Nome do Produto
   URL original: URL_QUE_FALHOU
   Tentando fallback: ./public/padrao.png
```

## Verificação Rápida

Execute este checklist:

- [ ] Backend está rodando em http://localhost:8000
- [ ] Arquivo `public/padrao.png` existe
- [ ] Consegue acessar http://localhost:8000/public/padrao.png no navegador
- [ ] Console do navegador mostra os logs de debug
- [ ] Aba Network mostra as requisições de imagem
- [ ] Testou com `test-product-images.html`

## Próximos Passos

Se o problema persistir após todas as correções:

1. **Compartilhe os logs do console** - Copie as mensagens de erro
2. **Compartilhe a aba Network** - Tire um screenshot das requisições falhando
3. **Verifique o banco de dados** - Confirme que `imagem_url` tem valores válidos
4. **Teste com imagens locais** - Coloque imagens na pasta `public/` e use URLs relativas

## Contato

Se precisar de ajuda adicional, forneça:
- Logs do console do navegador
- Screenshot da aba Network
- Output de `SELECT * FROM produtos_sessao LIMIT 1;`
- Versão do navegador e sistema operacional
