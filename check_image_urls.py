#!/usr/bin/env python3
"""
Script para verificar as URLs das imagens no banco de dados
"""

import sqlite3
import sys
from pathlib import Path

def check_database(db_path='backend_data.db'):
    """Verifica as URLs das imagens no banco de dados"""
    
    # Tentar diferentes localizações do banco
    possible_paths = [
        db_path,
        f'backend/{db_path}',
        f'./{db_path}'
    ]
    
    db_file = None
    for path in possible_paths:
        if Path(path).exists():
            db_file = path
            break
    
    if not db_file:
        print(f"❌ Banco de dados não encontrado!")
        print(f"   Procurado em: {possible_paths}")
        return False
    
    print(f"✅ Banco de dados encontrado: {db_file}\n")
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Verificar produtos na tabela produtos_sessao
        print("=" * 80)
        print("📦 PRODUTOS NA TABELA produtos_sessao")
        print("=" * 80)
        
        cursor.execute("""
            SELECT COUNT(*) FROM produtos_sessao
        """)
        total = cursor.fetchone()[0]
        print(f"\nTotal de produtos: {total}\n")
        
        if total == 0:
            print("⚠️ Nenhum produto encontrado na tabela produtos_sessao")
            print("   Isso é normal se nenhuma sessão foi criada ainda.\n")
        else:
            # Verificar URLs das imagens
            cursor.execute("""
                SELECT 
                    id,
                    descricao,
                    imagem_url,
                    CASE 
                        WHEN imagem_url IS NULL THEN 'NULL'
                        WHEN imagem_url = '' THEN 'VAZIO'
                        WHEN imagem_url LIKE 'http%' THEN 'EXTERNA'
                        WHEN imagem_url LIKE './%' THEN 'RELATIVA'
                        WHEN imagem_url LIKE '/%' THEN 'ABSOLUTA'
                        ELSE 'OUTRO'
                    END as tipo_url
                FROM produtos_sessao
                ORDER BY id
                LIMIT 20
            """)
            
            produtos = cursor.fetchall()
            
            print(f"{'ID':<5} {'Descrição':<40} {'Tipo URL':<10} {'URL'}")
            print("-" * 120)
            
            stats = {
                'NULL': 0,
                'VAZIO': 0,
                'EXTERNA': 0,
                'RELATIVA': 0,
                'ABSOLUTA': 0,
                'OUTRO': 0
            }
            
            for produto in produtos:
                id_prod, descricao, url, tipo = produto
                stats[tipo] += 1
                
                # Truncar descrição e URL para caber na tela
                desc_short = (descricao[:37] + '...') if len(descricao) > 40 else descricao
                url_short = (url[:60] + '...') if url and len(url) > 60 else (url or 'N/A')
                
                print(f"{id_prod:<5} {desc_short:<40} {tipo:<10} {url_short}")
            
            print("\n" + "=" * 80)
            print("📊 ESTATÍSTICAS")
            print("=" * 80)
            print(f"\nTotal de produtos analisados: {len(produtos)}")
            print(f"\nDistribuição de URLs:")
            for tipo, count in stats.items():
                if count > 0:
                    emoji = {
                        'NULL': '❌',
                        'VAZIO': '⚠️',
                        'EXTERNA': '🌐',
                        'RELATIVA': '📁',
                        'ABSOLUTA': '📂',
                        'OUTRO': '❓'
                    }.get(tipo, '•')
                    print(f"  {emoji} {tipo}: {count}")
            
            # Verificar problemas
            print("\n" + "=" * 80)
            print("🔍 DIAGNÓSTICO")
            print("=" * 80)
            
            problemas = []
            
            if stats['NULL'] > 0:
                problemas.append(f"⚠️ {stats['NULL']} produto(s) com imagem_url NULL")
            
            if stats['VAZIO'] > 0:
                problemas.append(f"⚠️ {stats['VAZIO']} produto(s) com imagem_url vazia")
            
            if stats['EXTERNA'] > 0:
                print(f"\n✅ {stats['EXTERNA']} produto(s) usando URLs externas (Unsplash, etc.)")
                print("   Isso é normal, mas pode haver problemas de CORS ou conectividade.")
            
            if stats['RELATIVA'] > 0:
                print(f"\n✅ {stats['RELATIVA']} produto(s) usando URLs relativas")
                print("   Certifique-se de que os arquivos existem na pasta public/")
            
            if stats['ABSOLUTA'] > 0:
                print(f"\n✅ {stats['ABSOLUTA']} produto(s) usando URLs absolutas")
            
            if problemas:
                print("\n⚠️ PROBLEMAS ENCONTRADOS:")
                for problema in problemas:
                    print(f"   {problema}")
                print("\n💡 SOLUÇÃO:")
                print("   Produtos sem imagem_url usarão a imagem padrão (padrao.png)")
                print("   O catálogo já está configurado para fazer isso automaticamente.")
            else:
                print("\n✅ Nenhum problema crítico encontrado!")
        
        # Verificar sessões
        print("\n" + "=" * 80)
        print("🔐 SESSÕES ATIVAS")
        print("=" * 80)
        
        cursor.execute("""
            SELECT 
                sessao_id,
                cliente_nome,
                status,
                COUNT(ps.id) as num_produtos
            FROM sessoes s
            LEFT JOIN produtos_sessao ps ON s.id = ps.sessao_uuid
            GROUP BY s.id
            ORDER BY s.criado_em DESC
            LIMIT 10
        """)
        
        sessoes = cursor.fetchall()
        
        if sessoes:
            print(f"\n{'Session ID':<40} {'Cliente':<20} {'Status':<12} {'Produtos'}")
            print("-" * 100)
            for sessao in sessoes:
                sid, nome, status, num_prods = sessao
                print(f"{sid:<40} {nome:<20} {status:<12} {num_prods}")
        else:
            print("\n⚠️ Nenhuma sessão encontrada")
        
        conn.close()
        
        print("\n" + "=" * 80)
        print("✅ Verificação concluída!")
        print("=" * 80)
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Erro ao acessar banco de dados: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'backend_data.db'
    success = check_database(db_path)
    sys.exit(0 if success else 1)
