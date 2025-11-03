-- Script SQL para adicionar campo imagem na tabela banners
-- Execute este script no seu banco Supabase

-- 1. Adicionar coluna imagem_url na tabela banners
ALTER TABLE banners 
ADD COLUMN imagem_url TEXT;

-- 2. Adicionar comentário para documentar o campo
COMMENT ON COLUMN banners.imagem_url IS 'URL da imagem do banner (opcional). Se não fornecida, será usado o layout de texto padrão.';

-- 3. Criar índice para otimizar consultas por banners com imagem
CREATE INDEX IF NOT EXISTS idx_banners_imagem_url ON banners(imagem_url) WHERE imagem_url IS NOT NULL;

-- 4. Atualizar a política RLS (Row Level Security) se necessário
-- Verificar se a política atual já permite SELECT na nova coluna
-- (Geralmente não é necessário alterar se a política usa SELECT *)

-- 5. Exemplo de inserção de banner com imagem
-- INSERT INTO banners (
--     titulo, 
--     descricao, 
--     tipo_promocao, 
--     valor_desconto, 
--     ativo, 
--     ordem, 
--     imagem_url
-- ) VALUES (
--     'Super Promoção de Verão', 
--     'Até 50% OFF em produtos selecionados', 
--     'desconto_percentual', 
--     50, 
--     true, 
--     1, 
--     'https://exemplo.com/banner-verao.jpg'
-- );

-- 6. Verificar a estrutura atualizada da tabela
-- SELECT column_name, data_type, is_nullable, column_default 
-- FROM information_schema.columns 
-- WHERE table_name = 'banners' 
-- ORDER BY ordinal_position;