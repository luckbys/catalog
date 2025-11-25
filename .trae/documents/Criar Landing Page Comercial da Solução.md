## Objetivos
- Criar uma landing page comercial que gere leads e mostre valor da solução.
- Destacar que a automação de IA (workflowIO) já está integrada ao catálogo.

## Estrutura de Conteúdo
- Hero: headline, subtítulo, bullets de valor e CTAs (demo, WhatsApp, falar com vendas).
- Como funciona: visão em 4 passos (catálogo → carrinho → entrega → automações).
- Funcionalidades: catálogo, carrinho, WhatsApp, follow‑up/encerramento, painel do entregador, n8n/webhook.
- Automação de IA (destaque): seção dedicada explicando workflowIO.
- Planos e preços: tabelas com recursos por plano.
- Prova social: depoimentos/casos e métricas.
- FAQ: implantação, prazos, suporte, LGPD.
- Contato: formulário simples + botão WhatsApp.

## Destaque: Automação de IA (workflowIO)
- Mensagem principal: “Automação inteligente integrada: qualifique leads, personalize mensagens e aumente conversões”.
- Bullets:
  - Qualificação e score de leads.
  - Mensagens personalizadas (WhatsApp/e‑mail) com tom e contexto da marca.
  - Sequências de follow‑ups e encerramento automático já operando no seu catálogo.
  - Integrações: Supabase, n8n/webhook, Evolution API.
- Visual: diagrama simples dos fluxos (lead → enrich/score → mensagem → follow‑up/encerrar).
- CTA contextual: “Agendar demo da automação”.

## CTAs
- Primário: “Agendar demo”.
- Secundário: “Falar no WhatsApp”.
- Apoio: “Ver catálogo de exemplo”.

## Captação de Leads
- Formulário com LGPD (nome, e‑mail, telefone, empresa, mensagem, consentimento).
- Envio: integrar com fluxo atual de leads (sem mudanças no backend, apenas consumo do endpoint existente).

## SEO e Performance
- Metas e Open Graph, JSON‑LD (SoftwareApplication/LocalBusiness), favicon.
- Imagens otimizadas, lazyload; fontes Inter.

## Analytics
- GA4 com eventos `lead_submit`, `cta_whatsapp_click`, `demo_view`.

## Design e UI
- Reaproveitar `public/styles.css` e `public/mobile.css`.
- Gradiente `header-gradient`, componentes responsivos mobile‑first.

## Implementação (somente landing)
- Criar `landing.html` (estático) consumindo assets já existentes.
- Incluir seção “Automação de IA” com copy e diagrama.
- Formulário postando no endpoint de leads já disponível.
- Links para catálogo demo e WhatsApp.

## Roteiro
- Fase 1: landing com seções e CTAs; formulário ligado ao fluxo atual.
- Fase 2: SEO/analytics avançado; prova social/casos.
- Fase 3: página de planos detalhada e materiais de mídia.

## Entregáveis
- `landing.html` (hero, seções, IA, planos, FAQ, contato).
- Copys e assets (logos, ícones, screenshots/diagrama).
- Configuração de analytics/SEO.

## Próximos Passos
- Aprovar a estrutura e as copys da seção de IA.
- Implementar a página e publicar para testes de conversão.