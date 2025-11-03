#!/usr/bin/env python3
"""
Script para corrigir URLs de imagens quebradas no banco de dados
"""

import sqlite3
from pathlib import Path
import sys

# Mapeamento de URLs quebradas para URLs funcionais
URL_FIXES = {
    'https://example.com/galaxy-s23.jpg': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400',
    'https://example.com/dell-inspiron.jpg': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400',
    'https://example.com/vitamina-d3.jpg': 'https://images.unsplash.com/photo-1550572017-4a6e8e8e4e8e?w=400',
    'https://example.com/isilax.jpg': 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400',
    # Corrigir URL do Unsplash que retorna 404
    'https://images.unsplash.com/photo-1550572017-4a6e8e8e4e8e?w=400': 'https://images.unsplash.com/photo-1471864190281-a93a3070b6de?w=400',
}

def fix_image_urls(db_path='backend_data.db', dry_run=False):
    """Corrige URLs de imagens quebradas"""
    
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
        return False
    
    print(f"✅ Banco de dados encontrado: {db_file}\n")
    
    if dry_run:
        print("🔍 MODO DRY-RUN (nenhuma alteração será feita)\n")
    else:
        print("⚠️ MODO DE CORREÇÃO (alterações serão aplicadas)\n")
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        print("=" * 100)
        print("🔧 CORREÇÕES A SEREM APLICADAS")
        print("=" * 100)
        
        total_fixes = 0
        
        for broken_url, fixed_url in URL_FIXES.items():
            # Verificar quantos produtos usam essa URL
            cursor.execute("""
                SELECT COUNT(*) FROM produtos_sessao
                WHERE imagem_url = ?
            """, (broken_url,))
            
            count = cursor.fetchone()[0]
            
            if count > 0:
                print(f"\n🔧 URL Quebrada: {broken_url}")
                print(f"   ✅ Nova URL: {fixed_url}")
                print(f"   📦 Produtos afetados: {count}")
                
                if not dry_run:
                    cursor.execute("""
                        UPDATE produtos_sessao
                        SET imagem_url = ?
                        WHERE imagem_url = ?
                    """, (fixed_url, broken_url))
                    
                    print(f"   ✅ Atualizado!")
                
                total_fixes += count
        
        if total_fixes == 0:
            print("\n✅ Nenhuma URL quebrada encontrada!")
        else:
            print("\n" + "=" * 100)
            print(f"📊 Total de produtos corrigidos: {total_fixes}")
            print("=" * 100)
            
            if not dry_run:
                conn.commit()
                print("\n✅ Alterações salvas no banco de dados!")
            else:
                print("\n💡 Execute sem --dry-run para aplicar as correções")
        
        # Verificar se ainda há URLs problemáticas
        print("\n" + "=" * 100)
        print("🔍 VERIFICANDO URLs RESTANTES")
        print("=" * 100)
        
        cursor.execute("""
            SELECT DISTINCT imagem_url, COUNT(*) as count
            FROM produtos_sessao
            WHERE imagem_url LIKE '%example.com%'
            GROUP BY imagem_url
        """)
        
        remaining = cursor.fetchall()
        
        if remaining:
            print("\n⚠️ URLs do example.com ainda presentes:")
            for url, count in remaining:
                print(f"   • {url} ({count} produto(s))")
            print("\n💡 Adicione essas URLs ao script para corrigi-las")
        else:
            print("\n✅ Nenhuma URL do example.com encontrada!")
        
        conn.close()
        
        print("\n" + "=" * 100)
        print("✅ Processo concluído!")
        print("=" * 100)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Corrige URLs de imagens quebradas')
    parser.add_argument('--db', default='backend_data.db', help='Caminho do banco de dados')
    parser.add_argument('--dry-run', action='store_true', help='Apenas simula as correções sem aplicá-las')
    
    args = parser.parse_args()
    
    success = fix_image_urls(args.db, args.dry_run)
    sys.exit(0 if success else 1)
