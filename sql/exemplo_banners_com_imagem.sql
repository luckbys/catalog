-- Exemplos de banners com imagem para testar a nova funcionalidade
-- Execute estes comandos no seu banco Supabase após aplicar o update_banners_add_image.sql

-- 1. Banner com imagem de promoção de verão
INSERT INTO banners (
    titulo, 
    descricao, 
    tipo_promocao, 
    valor_desconto, 
    percentual_desconto,
    ativo, 
    ordem, 
    imagem_url,
    badge_texto,
    cor_primaria,
    cor_secundaria
) VALUES (
    'Mega Promoção de Verão 2024', 
    'Descontos imperdíveis em toda a loja! Aproveite enquanto durarem os estoques.', 
    'desconto_percentual', 
    NULL,
    50, 
    true, 
    1, 
    'https://images.unsplash.com/photo-1441986300917-64674bd600d8?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80',
    '🔥 SUPER OFERTA',
    '#FF6B6B',
    '#4ECDC4'
);

-- 2. Banner com imagem de frete grátis
INSERT INTO banners (
    titulo, 
    descricao, 
    tipo_promocao, 
    valor_desconto, 
    ativo, 
    ordem, 
    imagem_url,
    badge_texto
) VALUES (
    'Frete Grátis para Todo Brasil', 
    'Em compras acima de R$ 99,00. Válido por tempo limitado!', 
    'frete_gratis', 
    99.00, 
    true, 
    2, 
    'https://images.unsplash.com/photo-1566576912321-d58ddd7a6088?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80',
    '📦 FRETE GRÁTIS'
);

-- 3. Banner com imagem de produtos em destaque
INSERT INTO banners (
    titulo, 
    descricao, 
    tipo_promocao, 
    ativo, 
    ordem, 
    imagem_url,
    badge_texto
) VALUES (
    'Novidades da Semana', 
    'Confira os produtos que acabaram de chegar na nossa loja!', 
    'promocional', 
    true, 
    3, 
    'https://images.unsplash.com/photo-1472851294608-062f824d29cc?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80',
    '✨ NOVIDADES'
);

-- 4. Banner sem imagem (para testar fallback)
INSERT INTO banners (
    titulo, 
    descricao, 
    tipo_promocao, 
    percentual_desconto,
    ativo, 
    ordem, 
    badge_texto,
    cor_primaria,
    cor_secundaria,
    icone
) VALUES (
    'Oferta Relâmpago', 
    'Apenas hoje! Não perca esta oportunidade única.', 
    'desconto_percentual',
    30, 
    true, 
    4, 
    '⚡ RELÂMPAGO',
    '#8B5CF6',
    '#EC4899',
    'zap'
);

-- Verificar os banners inseridos
SELECT id, titulo, tipo_promocao, imagem_url, ativo, ordem 
FROM banners 
ORDER BY ordem;