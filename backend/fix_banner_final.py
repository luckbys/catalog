#!/usr/bin/env python3
"""
Script para corrigir o problema da imagem do banner usando as configurações corretas
"""

import os

# Configurar as variáveis de ambiente diretamente (mesmas do servidor)
os.environ['SUPABASE_URL'] = 'https://chatbot-supabase1.zv7gpn.easypanel.host'
# A SUPABASE_KEY será necessária, mas vou tentar sem ela primeiro

try:
    from supabase import create_client, Client
except ImportError:
    print("❌ Supabase não instalado. Instalando...")
    import subprocess
    subprocess.check_call(["pip", "install", "supabase"])
    from supabase import create_client, Client

def fix_banner_final():
    print("🔧 Corrigindo problema da imagem do banner...")
    
    # Usar as mesmas configurações do servidor
    supabase_url = 'https://chatbot-supabase1.zv7gpn.easypanel.host'
    
    # Vou tentar descobrir a key do arquivo de configuração ou usar uma abordagem diferente
    print("⚠️ Preciso da SUPABASE_KEY para continuar...")
    print("💡 Vou tentar uma abordagem alternativa via API...")
    
    # Como a API está funcionando, vou usar curl para fazer a atualização
    import subprocess
    import json
    
    try:
        # Primeiro, vamos verificar se conseguimos acessar a API de banners
        print("\n1️⃣ Testando acesso à API...")
        result = subprocess.run([
            'curl', '-s', 'http://localhost:8000/api/banners'
        ], capture_output=True, text=True, shell=True)
        
        if result.returncode == 0:
            print("✅ API acessível!")
            data = json.loads(result.stdout)
            banners = data.get('banners', [])
            
            # Encontrar o banner problemático
            banner_problema = None
            for banner in banners:
                if banner.get('id') == 7:
                    banner_problema = banner
                    break
            
            if banner_problema:
                print(f"🎯 Banner encontrado: {banner_problema.get('titulo')}")
                print(f"🖼️ URL atual: {banner_problema.get('imagem_url')}")
                
                if banner_problema.get('imagem_url'):
                    print("\n2️⃣ Banner tem imagem problemática confirmada!")
                    print("💡 Como não posso atualizar via API (não há endpoint PUT),")
                    print("   vou criar um endpoint temporário ou usar outra abordagem...")
                    return True
                else:
                    print("✅ Banner já está sem imagem!")
                    return True
            else:
                print("❌ Banner ID 7 não encontrado")
                return False
        else:
            print(f"❌ Erro ao acessar API: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    success = fix_banner_final()
    if success:
        print("\n✅ Diagnóstico concluído!")
        print("🔄 Próximo passo: Implementar correção via endpoint temporário")
    else:
        print("\n❌ Falha no diagnóstico")