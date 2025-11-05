# 📐 Tamanhos Exatos do Banner - Guia de Design

## 🎯 Tamanhos Recomendados para Criação de Imagens

### 📱 **MOBILE (Smartphones)**

#### Tamanho Ideal:
```
Largura: 1080px
Altura: 607px
Proporção: 16:9
Formato: JPG ou PNG
Peso máximo: 300KB
```

#### Área Segura (Safe Area):
```
Margem superior: 80px
Margem inferior: 120px (para overlay de texto)
Margens laterais: 60px
```

#### Resolução Mínima:
```
Largura: 720px
Altura: 405px
```

---

### 📱 **TABLET**

#### Tamanho Ideal:
```
Largura: 1920px
Altura: 823px
Proporção: 21:9
Formato: JPG ou PNG
Peso máximo: 400KB
```

#### Área Segura:
```
Margem superior: 100px
Margem inferior: 150px
Margens laterais: 100px
```

---

### 💻 **DESKTOP**

#### Tamanho Ideal:
```
Largura: 2560px
Altura: 1024px
Proporção: 2.5:1
Formato: JPG ou PNG
Peso máximo: 500KB
```

#### Área Segura:
```
Margem superior: 120px
Margem inferior: 180px
Margens laterais: 150px
```

---

## 🎨 **TAMANHO UNIVERSAL (Recomendado)**

Para uma única imagem que funcione bem em todos os dispositivos:

```
Largura: 1920px
Altura: 1080px
Proporção: 16:9
Formato: JPG (qualidade 85%)
Peso máximo: 400KB
```

### Por que 1920x1080?
- ✅ Funciona perfeitamente em mobile (16:9)
- ✅ Compatível com tablet (será cortado nas laterais)
- ✅ Adequado para desktop (será cortado nas laterais)
- ✅ Tamanho de arquivo gerenciável
- ✅ Boa qualidade visual

---

## 📊 Tabela Comparativa

| Dispositivo | Largura | Altura | Proporção | Peso Max | Prioridade |
|-------------|---------|--------|-----------|----------|------------|
| **Mobile** | 1080px | 607px | 16:9 | 300KB | ⭐⭐⭐ Alta |
| **Tablet** | 1920px | 823px | 21:9 | 400KB | ⭐⭐ Média |
| **Desktop** | 2560px | 1024px | 2.5:1 | 500KB | ⭐⭐ Média |
| **Universal** | 1920px | 1080px | 16:9 | 400KB | ⭐⭐⭐ Alta |

---

## 🎯 Área de Foco (Safe Zone)

### Onde colocar elementos importantes:

```
┌─────────────────────────────────────┐
│ ← 60px →                  ← 60px → │
│ ↑                                   │
│ 80px    ┌─────────────────┐         │
│ ↓       │                 │         │
│         │  ÁREA SEGURA    │         │
│         │  (Texto/Logo)   │         │
│         │                 │         │
│ ↑       └─────────────────┘         │
│ 120px                               │
│ ↓                                   │
└─────────────────────────────────────┘
```

### Elementos Importantes:
- **Logo**: Canto superior esquerdo (80px do topo, 60px da lateral)
- **Título Principal**: Centro ou esquerda (mínimo 80px do topo)
- **CTA/Botão**: Inferior esquerdo (mínimo 120px da base)
- **Preço/Desconto**: Superior direito ou inferior direito

---

## 🎨 Especificações Técnicas

### Formato de Arquivo:

#### JPG (Recomendado para fotos):
```
Qualidade: 80-85%
Compressão: Progressive
Perfil de cor: sRGB
```

#### PNG (Para imagens com transparência):
```
Compressão: PNG-8 ou PNG-24
Transparência: Suportada
Perfil de cor: sRGB
```

#### WebP (Melhor performance):
```
Qualidade: 80%
Compressão: Lossy
Suporte: Moderno
```

### Otimização:
- ✅ Usar ferramentas como TinyPNG ou ImageOptim
- ✅ Remover metadados EXIF
- ✅ Converter para sRGB
- ✅ Redimensionar antes de comprimir

---

## 📱 Tamanhos por Resolução de Tela

### iPhone SE (375px de largura):
```
Banner renderizado: 375px × 211px
Imagem ideal: 750px × 422px (2x)
```

### iPhone 12/13/14 (390px de largura):
```
Banner renderizado: 390px × 219px
Imagem ideal: 780px × 438px (2x)
```

### Samsung Galaxy S20 (360px de largura):
```
Banner renderizado: 360px × 203px
Imagem ideal: 720px × 405px (2x)
```

### iPad (768px de largura):
```
Banner renderizado: 768px × 329px
Imagem ideal: 1536px × 658px (2x)
```

### Desktop HD (1920px de largura):
```
Banner renderizado: 1920px × 768px
Imagem ideal: 2560px × 1024px
```

---

## 🎨 Templates de Design

### Photoshop/Figma:

#### Mobile (16:9):
```
Novo Documento:
- Largura: 1080px
- Altura: 607px
- Resolução: 72 DPI (web) ou 144 DPI (retina)
- Modo de cor: RGB
```

#### Desktop (2.5:1):
```
Novo Documento:
- Largura: 2560px
- Altura: 1024px
- Resolução: 72 DPI
- Modo de cor: RGB
```

#### Universal (16:9):
```
Novo Documento:
- Largura: 1920px
- Altura: 1080px
- Resolução: 72 DPI
- Modo de cor: RGB
```

---

## 📐 Guias de Layout (Guides)

### Para Photoshop/Figma:

```
Guias Verticais:
- 60px (margem esquerda)
- 1020px (margem direita para 1080px)
- 1860px (margem direita para 1920px)

Guias Horizontais:
- 80px (margem superior)
- 487px (margem inferior para 607px)
- 900px (margem inferior para 1080px)
```

---

## 🎯 Checklist de Design

### Antes de Exportar:

- [ ] Imagem tem pelo menos 1080px de largura
- [ ] Proporção é 16:9 (ou próxima)
- [ ] Elementos importantes estão na área segura
- [ ] Texto é legível em mobile (mínimo 24px)
- [ ] Contraste adequado (mínimo 4.5:1)
- [ ] Arquivo otimizado (< 400KB)
- [ ] Formato correto (JPG/PNG/WebP)
- [ ] Testado em diferentes tamanhos

---

## 💡 Dicas de Design

### 1. **Composição**:
- Elementos principais no centro ou esquerda
- Evitar texto muito próximo das bordas
- Usar regra dos terços

### 2. **Tipografia**:
- Tamanho mínimo: 24px (mobile)
- Fonte legível (sans-serif)
- Contraste alto com fundo
- Sombra ou outline para legibilidade

### 3. **Cores**:
- Usar paleta consistente
- Alto contraste para CTAs
- Evitar cores muito saturadas
- Testar em diferentes telas

### 4. **Elementos**:
- Logo: 80-120px de altura
- Título: 48-72px
- Subtítulo: 24-36px
- CTA: 40-56px de altura

---

## 📊 Exemplos de Dimensões

### Banner de Promoção:
```
Tamanho: 1920px × 1080px
Logo: 100px altura (canto superior esquerdo)
Título: 72px ("50% OFF")
Subtítulo: 36px ("Em todos os produtos")
CTA: 48px altura × 200px largura
Peso: 350KB
```

### Banner de Produto:
```
Tamanho: 1920px × 1080px
Produto: 60% da largura (direita)
Texto: 40% da largura (esquerda)
Título: 64px
Descrição: 28px
Preço: 56px (destaque)
Peso: 280KB
```

### Banner Institucional:
```
Tamanho: 1920px × 1080px
Imagem de fundo: 100%
Overlay: Gradiente escuro (40% opacidade)
Título: 80px (centralizado)
Subtítulo: 32px
Logo: 120px altura (centro)
Peso: 420KB
```

---

## 🔧 Ferramentas Recomendadas

### Design:
- **Figma** (gratuito, online)
- **Canva** (templates prontos)
- **Photoshop** (profissional)
- **GIMP** (gratuito, desktop)

### Otimização:
- **TinyPNG** (compressão online)
- **ImageOptim** (Mac)
- **Squoosh** (Google, online)
- **Sharp** (Node.js)

### Teste:
- **Chrome DevTools** (responsividade)
- **BrowserStack** (múltiplos dispositivos)
- **Responsively** (app desktop)

---

## 📱 Teste de Visualização

### Como testar seu banner:

1. **No navegador**:
```
http://localhost:8000/catalogo.html?sessao_id=XXX
```

2. **DevTools (F12)**:
- Clique no ícone de dispositivo móvel
- Teste em diferentes resoluções:
  - iPhone SE (375px)
  - iPhone 12 (390px)
  - iPad (768px)
  - Desktop (1920px)

3. **Verificar**:
- [ ] Imagem preenche todo o espaço
- [ ] Texto é legível
- [ ] Elementos importantes visíveis
- [ ] Carrega rápido (< 2s)

---

## 🎨 Template Pronto

### Baixe o template PSD/Figma:

```
Nome: banner-template-1920x1080.psd
Tamanho: 1920px × 1080px
Camadas:
- Fundo (imagem)
- Overlay (gradiente)
- Logo (smart object)
- Título (texto editável)
- Subtítulo (texto editável)
- CTA (botão editável)
- Guias (área segura)
```

---

## ✅ Resumo Rápido

### Para 90% dos casos, use:

```
📐 Tamanho: 1920px × 1080px
📊 Proporção: 16:9
💾 Formato: JPG (qualidade 85%)
⚖️ Peso: < 400KB
🎨 Área segura: 60px margens laterais, 80px topo, 120px base
```

### Exportar em:
1. **1920x1080** (principal)
2. **1080x607** (mobile otimizado) - opcional
3. **2560x1024** (desktop HD) - opcional

---

**Data:** 04/11/2025  
**Versão:** 1.0  
**Status:** ✅ Guia Completo
