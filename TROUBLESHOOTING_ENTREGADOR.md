# Troubleshooting - Link do Entregador

## Problema
Link `https://catalogo-hakim.zv7gpn.easypanel.host/entregador.html?pedido=123` não abre.

## Checklist de Verificação

### 1. ✅ URL está sendo construída corretamente
```
https://catalogo-hakim.zv7gpn.easypanel.host/entregador.html?pedido=123
```

### 2. ✅ Rota está registrada no backend
```python
@app.get("/entregador.html")
async def serve_entregador():
    """Serve a página do entregador"""
```

### 3. ⚠️ Arquivo precisa estar no lugar certo

#### Estrutura esperada:
```
projeto/
├── entregador.html          ← Deve estar aqui (raiz do projeto)
├── catalogo.html
├── status.html
├── admin-pedidos.html
└── backend/
    └── app.py
```

#### Verificar se arquivo existe:
```bash
# No diretório do projeto
ls -la entregador.html
```

### 4. ⚠️ Backend precisa estar rodando

#### Verificar se backend está ativo:
```bash
# Verificar processos
ps aux | grep uvicorn

# Ou verificar logs do Docker/EasyPanel
docker logs <container_name>
```

### 5. ⚠️ Deploy precisa incluir o arquivo

#### No EasyPanel/Docker, verificar:
- Arquivo `entregador.html` está no repositório?
- Dockerfile copia o arquivo?
- Deploy foi feito após criar o arquivo?

## Soluções

### Solução 1: Verificar se arquivo existe
```bash
# Listar arquivos HTML na raiz
ls -la *.html
```

**Esperado:**
```
-rw-r--r-- 1 user user  xxxxx entregador.html
-rw-r--r-- 1 user user  xxxxx catalogo.html
-rw-r--r-- 1 user user  xxxxx status.html
-rw-r--r-- 1 user user  xxxxx admin-pedidos.html
```

### Solução 2: Fazer commit e push do arquivo
```bash
# Adicionar arquivo ao git
git add entregador.html

# Commit
git commit -m "Add entregador.html page"

# Push para repositório
git push origin main
```

### Solução 3: Fazer redeploy no EasyPanel
1. Acesse o painel do EasyPanel
2. Vá para o serviço `catalogo-hakim`
3. Clique em "Redeploy" ou "Rebuild"
4. Aguarde o deploy completar

### Solução 4: Verificar logs do backend
```bash
# Ver logs em tempo real
docker logs -f <container_name>

# Ou no EasyPanel
# Ir em Logs → Ver logs do container
```

**Procurar por:**
```
[INFO] Application startup complete
[INFO] Uvicorn running on http://0.0.0.0:8000
```

### Solução 5: Testar localmente primeiro
```bash
# Iniciar backend local
cd backend
uvicorn app:app --reload --port 8000

# Em outro terminal, testar
curl http://localhost:8000/entregador.html
```

**Esperado:** HTML da página do entregador

## Teste Rápido

### 1. Testar se backend está respondendo
```bash
curl https://catalogo-hakim.zv7gpn.easypanel.host/health
```

**Esperado:**
```json
{"status":"ok","timestamp":"2024-..."}
```

### 2. Testar rota do entregador
```bash
curl https://catalogo-hakim.zv7gpn.easypanel.host/entregador.html?pedido=123
```

**Esperado:** HTML completo da página

**Se retornar 404:** Arquivo não está sendo servido
**Se retornar 500:** Erro no backend
**Se não responder:** Backend não está rodando

## Comandos Úteis

### Verificar estrutura de arquivos
```bash
# Listar todos os arquivos HTML
find . -name "*.html" -type f

# Ver estrutura do projeto
tree -L 2
```

### Verificar se backend está servindo arquivos
```bash
# Testar todas as rotas HTML
curl -I https://catalogo-hakim.zv7gpn.easypanel.host/catalogo.html
curl -I https://catalogo-hakim.zv7gpn.easypanel.host/status.html
curl -I https://catalogo-hakim.zv7gpn.easypanel.host/admin-pedidos.html
curl -I https://catalogo-hakim.zv7gpn.easypanel.host/entregador.html
```

## Próximos Passos

### Se arquivo não existe:
1. ✅ Arquivo `entregador.html` já foi criado
2. ⚠️ Fazer commit: `git add entregador.html && git commit -m "Add entregador page"`
3. ⚠️ Fazer push: `git push`
4. ⚠️ Redeploy no EasyPanel

### Se backend não está rodando:
1. Verificar logs do EasyPanel
2. Verificar se há erros no código
3. Reiniciar o serviço

### Se rota não está funcionando:
1. Verificar se `backend/app.py` tem a rota `@app.get("/entregador.html")`
2. Verificar se backend foi reiniciado após adicionar rota
3. Fazer redeploy

## Checklist Final

- [ ] Arquivo `entregador.html` existe na raiz do projeto
- [ ] Arquivo foi commitado no git
- [ ] Push foi feito para o repositório
- [ ] Redeploy foi feito no EasyPanel
- [ ] Backend está rodando (testar /health)
- [ ] Rota `/entregador.html` responde
- [ ] Link completo abre no navegador

## Teste Final

Abrir no navegador:
```
https://catalogo-hakim.zv7gpn.easypanel.host/entregador.html?pedido=49
```

**Deve mostrar:**
- 🗺️ Mapa com localização
- 👤 Informações do cliente
- 💳 Forma de pagamento
- 📦 Itens do pedido
- Botões de ação

## Contato de Suporte

Se nada funcionar:
1. Verificar logs completos do backend
2. Verificar configuração do EasyPanel
3. Verificar se domínio está apontando corretamente
4. Testar com `http://localhost:8000/entregador.html` localmente
