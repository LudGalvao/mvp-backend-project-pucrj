#!/usr/bin/env python3
"""
Script de instalação das otimizações de performance
Para API de Exercícios v2.0
"""
import subprocess
import sys
import os

def run_command(command, description):
    """Executa comando e mostra progresso"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Concluído!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro em {description}: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False

def main():
    print("🚀 INSTALAÇÃO DAS OTIMIZAÇÕES DE PERFORMANCE")
    print("🎯 API de Exercícios v2.0")
    print("=" * 60)
    
    # Lista de comandos de instalação
    commands = [
        ("pip install --upgrade pip", "Atualizando pip"),
        ("pip install httpx[http2]", "Instalando httpx com suporte HTTP/2"),
        ("pip install --upgrade fastapi", "Atualizando FastAPI"),
        ("pip install --upgrade pydantic", "Atualizando Pydantic"),
        ("pip install --upgrade uvicorn[standard]", "Atualizando Uvicorn"),
        ("pip install psutil", "Instalando monitor de sistema"),
    ]
    
    success_count = 0
    
    for command, description in commands:
        if run_command(command, description):
            success_count += 1
        print("-" * 40)
    
    print("\n📊 RESULTADO DA INSTALAÇÃO")
    print("=" * 60)
    print(f"✅ Sucesso: {success_count}/{len(commands)}")
    
    if success_count == len(commands):
        print("🎉 TODAS AS OTIMIZAÇÕES INSTALADAS COM SUCESSO!")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Reinicie o servidor: uvicorn app:app --reload")
        print("2. Teste a performance: python test_performance.py")
        print("3. Use o endpoint /exercicios/preload para cache inicial")
    else:
        print("⚠️  Algumas instalações falharam. Verifique os erros acima.")
    
    print("\n💡 DICAS DE PERFORMANCE:")
    print("• Use o preload no startup para cache inicial")
    print("• Monitore o cache com /exercicios/cache/status") 
    print("• Para produção, considere usar gunicorn")

if __name__ == "__main__":
    main() 