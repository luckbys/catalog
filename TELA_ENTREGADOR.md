# Tela do Entregador - Hakim Farma

## Resumo
Interface completa para entregadores com mapa interativo, informações do pedido, dados do cliente e ações rápidas para gerenciar entregas.

## Funcionalidades

### 🗺️ Mapa Interativo
- **Biblioteca**: Leaflet.js
- **Provedor de Mapas**: Geoapify
- **Geocodificação**: Converte endereço em coordenadas automaticamente
- **Marcador personalizado**: Ícone de localização no endereço de entrega
- **Popup**: Mostra nome do cliente e endereço ao clicar no marcador

### 📋 Informações do Pedido

#### Dados do Cliente
- Nome
- Telefone (clicável para ligar)
- Endereço completo
- Observações do pedido

#### Forma de Pagamento
- Método de pagamento com badge colorido:
  - 💵 Dinheiro (amarelo)
  - 💳 Cartão (azul/roxo)
  - 📱 PIX (azul claro)
- Status do pagamento (Pendente/Pago/Falhou/Reembolsado)

#### Itens do Pedido
- Lista completa de produtos
- Quantidade de cada item
- Preço unitário
- Total do pedido em destaque

### 🎯 Ações Rápidas

1. **Abrir Navegação** 🗺️
   - Abre Google Maps com rota até o cliente
   - Usa coordenadas geocodificadas

2. **Ligar para Cliente** 📞
   - Inicia chamada telefônica diretamente
   - Usa protocolo `tel:`

3. **Confirmar Entrega** ✅
   - Atualiza status para "delivered"
   - Envia para API
   - Confirmação visual

4. **Reportar Problema** ⚠️
   - Permite descrever problemas
   - Notifica central (TODO: implementar backend)

## Tecnologias Utilizadas

### Frontend
- **HTML5/CSS3**: Interface responsiva
- **Leaflet.js 1.9.4**: Biblioteca de mapas
- **Geoapify API**: Mapas e geocodificação
- **Vanilla JavaScript**: Lógica da aplicação

### APIs Integradas
- **Geoapify Geocoding API**: Converte endereços em coordenadas
- **Geoapify Maps API**: Tiles do mapa
- **Backend API**: Busca dados do pedido e atualiza status

## Configuração

### API Key Geoapify
```javascript
const GEOAPIFY_API_KEY = '2d2edc07a3ed4f97ae8264363fad3242';
```

### Endpoints Utilizados

#### GET /api/order-status
Busca informações completas do pedido
```
GET /api/order-status?order_id=123
```

#### PUT /api/orders/{id}/delivery-status
Atualiza status de entrega
```json
{
  "delivery_status": "delivered"
}
```

## Como Usar

### Acesso
```
http://localhost:8000/entregador.html?pedido=123
```

### Parâmetros URL
- `pedido` ou `order_id`: ID do pedido a ser entregue

### Fluxo de Uso

1. **Entregador acessa o link** com ID do pedido
2. **Mapa carrega** com localização do cliente
3. **Revisa informações**:
   - Endereço
   - Itens
   - Forma de pagamento
4. **Usa ações rápidas**:
   - Abre navegação para rota
   - Liga para cliente se necessário
5. **Confirma entrega** ao chegar no local
6. **Status atualizado** no sistema

## Design Responsivo

### Mobile (< 768px)
- Mapa: 400px altura
- Botões: Full width (empilhados)
- Layout otimizado para tela pequena

### Desktop (≥ 768px)
- Mapa: 500px altura
- Botões: Grid 2 colunas
- Mais espaçamento e conforto visual

## Componentes Visuais

### Header
- Logo da farmácia
- Badge de status "Em Rota" (pulsante)
- Sticky (fixo no topo)

### Cards
- Informações do Cliente
- Forma de Pagamento
- Itens do Pedido

### Badges
- Status de entrega
- Forma de pagamento (coloridos)
- Quantidade de itens

### Botões
- Primário (verde): Confirmar Entrega
- Secundário (branco): Navegação e Ligar
- Perigo (vermelho): Reportar Problema

## Geocodificação

### Como Funciona
```javascript
async function geocodeAddress(address) {
  const response = await fetch(
    `https://api.geoapify.com/v1/geocode/search?text=${address}&apiKey=${API_KEY}`
  );
  const data = await response.json();
  return { lat: coords[1], lng: coords[0] };
}
```

### Fallback
Se geocodificação falhar:
- Mapa mostra São Paulo (coordenadas padrão)
- Endereço ainda é exibido em texto
- Navegação pode não funcionar

## Melhorias Futuras

### Planejadas
- [ ] Tracking em tempo real da localização do entregador
- [ ] Rota otimizada com múltiplas entregas
- [ ] Chat com cliente
- [ ] Foto de comprovação de entrega
- [ ] Assinatura digital
- [ ] Histórico de entregas do dia
- [ ] Notificações push
- [ ] Modo offline

### Backend Necessário
- [ ] Endpoint para reportar problemas
- [ ] Endpoint para upload de fotos
- [ ] WebSocket para tracking em tempo real
- [ ] Sistema de notificações

## Segurança

### Considerações
- ✅ API Key exposta no frontend (limitada por domínio no Geoapify)
- ✅ Validação de order_id no backend
- ⚠️ TODO: Autenticação do entregador
- ⚠️ TODO: Verificar permissões (entregador só vê seus pedidos)

## Testes

### Testar Localmente
1. Inicie o backend
2. Acesse: `http://localhost:8000/entregador.html?pedido=123`
3. Verifique:
   - Mapa carrega
   - Dados do pedido aparecem
   - Botões funcionam
   - Geocodificação funciona

### Testar Geocodificação
```javascript
// No console do navegador
geocodeAddress('Av. Paulista, 1000, São Paulo').then(console.log);
```

## Troubleshooting

### Mapa não carrega
- Verificar API Key do Geoapify
- Verificar console para erros
- Testar conexão com internet

### Endereço não geocodifica
- Verificar formato do endereço
- Adicionar cidade/estado
- Usar endereço mais específico

### Botões não funcionam
- Verificar console para erros
- Verificar se order_id está na URL
- Verificar se backend está rodando

## Exemplo de Uso

```bash
# URL completa
http://localhost:8000/entregador.html?pedido=49

# Fluxo
1. Entregador recebe link via WhatsApp
2. Abre no celular
3. Vê mapa com localização
4. Clica "Abrir Navegação"
5. Google Maps abre com rota
6. Chega no local
7. Clica "Confirmar Entrega"
8. Status atualizado no sistema
```
