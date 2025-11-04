// LÓGICA DE DESCONTO EXTRAÍDA DE PRODUÇÃO
// URL: https://hakimfarma.devsible.com.br/catalogo.html?sessao_id=07ib2MEKsa

data.produtos.forEach(p => {

                // Usar endpoint local como fallback quando imagem_url for nula/vazia
                let imageUrl = p.imagem_url && p.imagem_url.trim() !== '' 
                    ? p.imagem_url 
                    : `${API_BASE}/api/local-image?path=padrao.png`;
                
                // Se a URL é do MinIO, usar o proxy do backend (mesmo que nos banners)
                if (imageUrl && imageUrl.includes('c4crm-minio.zv7gpn.easypanel.host')) {
                    // Extrair apenas o nome do arquivo da URL do MinIO
                    const urlParts = imageUrl.split('/');
                    const fileName = urlParts[urlParts.length - 1];
                    imageUrl = `${API_BASE}/api/minio-image?path=${fileName}`;
                    console.log('🔄 Usando proxy MinIO para produto:', p.descricao, '| arquivo:', fileName);
                }
                
                console.log('[DEBUG] Produto:', p.descricao, '| imagem_url:', p.imagem_url, '| URL final:', imageUrl);
                
                // Calcular preço promocional se houver desconto
                let originalPrice = null;
                let promoPrice = null;
                
                if (p.preco_original && (p.percentual_desconto || p.valor_desconto)) {
                    originalPrice = Number(p.preco_original);
                    promoPrice = Number(p.preco);
                } else if (p.percentual_desconto && p.percentual_desconto > 0) {
                    // Se só temos percentual de desconto, calcular preço original
                    originalPrice = Number(p.preco) / (1 - (p.percentual_desconto / 100));
                    promoPrice = Number(p.preco);
                } else if (p.valor_desconto && p.valor_desconto > 0) {
                    // Se só temos valor de desconto, calcular preço original
                    originalPrice = Number(p.preco) + Number(p.valor_desconto);
                    promoPrice = Number(p.preco);
                }
                
                productsData.push({
                    id: String(p.id),
                    name: p.descricao,
                    description: p.apresentacao || p.categoria || p.descricao,
                    price: Number(p.preco),
                    originalPrice: originalPrice,
                    promoPrice: promoPrice,
                    percentualDesconto: p.percentual_desconto ? Number(p.percentual_desconto) : null,
                    valorDesconto: p.valor_desconto ? Number(p.valor_desconto) : null,
                    imageUrl: imageUrl,
                    laboratorio: p.laboratorio
                
});