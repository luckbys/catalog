#!/usr/bin/env python3
"""
Script para testar se as URLs das imagens estão acessíveis
"""

import sqlite3
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys

def test_url(url, timeout=5):
    """Testa se uma URL está acessível"""
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        return {
            'url': url,
            'status': response.status_code,
            'ok': response.status_code == 200,
            'error': None
        }
    except requests.exceptions.Timeout:
        return {
            'url': url,
            'status': None,
            'ok': False,
            'error': 'Timeout'
        }
    except requests.exceptions.ConnectionError:
        return {
            'url': url,
            'status': None,
            'ok': False,
            'error': 'Connection Error'
        }
    except Exception as e:
        return {
            'url': url,
            'status': None,
            'ok': False,
            'error': str(e)
        }

def check_image_urls(db_path='backend_data.db', max_workers=5):
    """Verifica se as URLs das imagens estão acessíveis"""
    
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
    print("🔍 Testando URLs das imagens...\n")
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Buscar URLs únicas
        cursor.execute("""
            SELECT DISTINCT imagem_url, COUNT(*) as count
            FROM produtos_sessao
            WHERE imagem_url IS NOT NULL AND imagem_url != ''
            GROUP BY imagem_url
            ORDER BY count DESC
        """)
        
        urls = cursor.fetchall()
        conn.close()
        
        if not urls:
            print("⚠️ Nenhuma URL encontrada")
            return True
        
        print(f"📊 Total de URLs únicas: {len(urls)}\n")
        print("=" * 100)
        
        results = []
        
        # Testar URLs em paralelo
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(test_url, url[0]): url for url in urls}
            
            for future in as_completed(future_to_url):
                url_data = future_to_url[future]
                url, count = url_data
                
                try:
                    result = future.result()
                    result['count'] = count
                    results.append(result)
                    
                    # Exibir resultado
                    status_emoji = '✅' if result['ok'] else '❌'
                    status_text = f"HTTP {result['status']}" if result['status'] else result['error']
                    
                    # Truncar URL para caber na tela
                    url_short = (url[:70] + '...') if len(url) > 70 else url
                    
                    print(f"{status_emoji} [{status_text:>20}] {url_short} (usado por {count} produto(s))")
                    
                except Exception as e:
                    print(f"❌ Erro ao testar {url}: {e}")
        
        # Estatísticas
        print("\n" + "=" * 100)
        print("📊 ESTATÍSTICAS")
        print("=" * 100)
        
        total = len(results)
        ok = sum(1 for r in results if r['ok'])
        failed = total - ok
        
        print(f"\nTotal de URLs testadas: {total}")
        print(f"✅ Acessíveis: {ok} ({ok/total*100:.1f}%)")
        print(f"❌ Inacessíveis: {failed} ({failed/total*100:.1f}%)")
        
        # URLs problemáticas
        if failed > 0:
            print("\n" + "=" * 100)
            print("⚠️ URLs PROBLEMÁTICAS")
            print("=" * 100)
            
            for result in results:
                if not result['ok']:
                    url_short = (result['url'][:70] + '...') if len(result['url']) > 70 else result['url']
                    error = result['error'] or f"HTTP {result['status']}"
                    print(f"\n❌ {url_short}")
                    print(f"   Erro: {error}")
                    print(f"   Usado por: {result['count']} produto(s)")
            
            print("\n💡 RECOMENDAÇÕES:")
            print("   1. Substitua URLs do example.com por URLs válidas")
            print("   2. Verifique se há problemas de conectividade com Unsplash")
            print("   3. Considere usar imagens locais na pasta public/")
            print("   4. O catálogo usará a imagem padrão (padrao.png) para URLs que falharem")
        else:
            print("\n✅ Todas as URLs estão acessíveis!")
        
        print("\n" + "=" * 100)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'backend_data.db'
    
    # Verificar se requests está instalado
    try:
        import requests
    except ImportError:
        print("❌ Módulo 'requests' não encontrado!")
        print("   Instale com: pip install requests")
        sys.exit(1)
    
    success = check_image_urls(db_path)
    sys.exit(0 if success else 1)
