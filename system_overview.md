# Panorama Geral do Sistema

Este documento fornece uma visão geral técnica e funcional do sistema de Catálogo e Gestão de Pedidos.

## 1. Visão Geral
O sistema é uma plataforma completa de e-commerce simplificado, focado em permitir que clientes visualizem produtos, montem carrinhos e enviem pedidos via WhatsApp ou API. Possui um painel administrativo robusto para gestão de pedidos, banners promocionais e configurações de instâncias.

## 2. Arquitetura

### Frontend
- **Tecnologia**: HTML5, JavaScript (Vanilla), Tailwind CSS.
- **Design**: "Glassmorphism" premium, responsivo, com suporte a Dark Mode.
- **Bibliotecas**: Font Awesome (ícones), Google Fonts (Inter).
- **Arquivos Principais**:
    - `catalogo.html`: Interface pública para clientes.
    - `admin-pedidos.html`: Painel de gestão de pedidos em tempo real.
    - `admin-banners.html`: Gestão de banners promocionais.
    - `admin-config.html`: Configurações gerais do sistema.
    - `admin-instancias.html`: Gerenciamento de instâncias de atendimento.
    - `entregador.html`: Interface para entregadores.

### Backend
- **Framework**: FastAPI (Python).
- **Servidor**: Uvicorn.
- **Arquivo Principal**: `backend/app.py`.
- **Funcionalidades**:
    - API RESTful para CRUD de pedidos, produtos e banners.
    - Proxy de imagens (MinIO/External) para contornar problemas de CORS/HTTPS.
    - Integração com Supabase para persistência de dados.
    - Webhooks para integração com Evolution API (WhatsApp).

### Banco de Dados & Armazenamento
- **Banco de Dados**: Supabase (PostgreSQL).
- **Storage**: MinIO (S3 Compatible) para armazenamento de imagens de produtos e banners.

### Infraestrutura
- **Containerização**: Docker e Docker Compose.
- **Servidor Web**: Nginx (Reverse Proxy).

## 3. Módulos Principais

### 🛒 Catálogo Público (`catalogo.html`)
- Listagem de produtos com categorias.
- Carrinho de compras interativo.
- Checkout com integração via WhatsApp.
- Exibição de banners promocionais dinâmicos.

### 📊 Painel Administrativo
#### Gestão de Pedidos (`admin-pedidos.html`)
- **Visualização Kanban/Lista**: Monitoramento de pedidos por status (Pendente, Confirmado, Em Entrega, Entregue).
- **Ações Rápidas**: Aceitar, Recusar, Enviar, Confirmar Entrega.
- **Filtros**: Por status e busca por ID.
- **Notificações**: Toasts para feedback de ações.
- **Design**: Layout premium com Dark Mode e atualização em tempo real (polling).

#### Gestão de Banners (`admin-banners.html`)
- **CRUD Completo**: Criar, Editar, Excluir e Alternar status de banners.
- **Preview em Tempo Real**: Visualização imediata de como o banner ficará no catálogo.
- **Upload/Proxy**: Suporte a URLs externas e imagens do MinIO via proxy.

#### Configurações e Instâncias
- **`admin-config.html`**: Ajustes globais do sistema.
- **`admin-instancias.html`**: Controle de instâncias de conexão (ex: WhatsApp Sessions).

### 🚚 Módulo de Entrega (`entregador.html`)
- Interface dedicada para entregadores visualizarem rotas e status de entregas.

## 4. Status Atual e Melhorias Recentes
- **UI Premium**: Implementação de design system consistente (Glassmorphism + Tailwind) em todo o painel administrativo.
- **Dark Mode**: Suporte nativo a tema escuro em `admin-pedidos.html` e `admin-banners.html`.
- **Correções Críticas**:
    - Fixação do proxy de imagens para banners (`/api/proxy-image`).
    - Restauração da funcionalidade de `admin-pedidos.html` após corrupção de arquivo.
    - Padronização da barra de navegação entre as páginas administrativas.

## 5. Próximos Passos Sugeridos
- Implementar autenticação/login para proteger as rotas administrativas.
- Adicionar métricas e dashboards mais detalhados em `admin-pedidos.html`.
- Otimizar o carregamento de imagens no catálogo (lazy loading).
