# 🚀 Quick Fix - Imagens Quebradas

## ⚡ Solução Rápida (1 minuto)

Se as imagens dos produtos não estão aparecendo:

```bash
# 1. Verificar o problema
python test_image_urls.py

# 2. Corrigir automaticamente
python fix_broken_image_urls.py

# 3. Verificar novamente
python test_image_urls.py
```

**Pronto!** As imagens devem estar funcionando agora.

## 🔍 Testar Visualmente

Abra no navegador:
```
http://localhost:8000/test-product-images.html?sessao_id=SEU_SESSION_ID
```

## 📋 Checklist Rápido

- [ ] Backend rodando em `http://localhost:8000`
- [ ] Arquivo `public/padrao.png` existe
- [ ] Executou `python fix_broken_image_urls.py`
- [ ] Testou no navegador

## 🆘 Ainda não funciona?

1. Verifique o console do navegador (F12)
2. Veja os logs: `[DEBUG] Produto: ... | imagem_url: ...`
3. Leia a documentação completa: `SOLUCAO_IMAGENS.md`

## 📚 Documentação Completa

- `SOLUCAO_IMAGENS.md` - Solução detalhada
- `DEBUG_IMAGENS.md` - Guia de diagnóstico
- `test-product-images.html` - Teste visual
