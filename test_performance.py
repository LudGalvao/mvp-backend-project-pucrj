#!/usr/bin/env python3
"""
Script para testar performance das otimizações implementadas
"""
import asyncio
import time
import httpx
import json
from typing import List, Dict
import statistics

# Configurações do teste
BASE_URL = "http://localhost:8000"
NUM_TESTS = 10

async def test_exercise_generation_performance():
    """Testa a performance da geração de exercícios"""
    print("🧪 Testando Performance da Geração de Exercícios\n")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response_times = []
        
        for i in range(NUM_TESTS):
            print(f"📊 Teste {i+1}/{NUM_TESTS}")
            
            start_time = time.time()
            
            try:
                response = await client.post(f"{BASE_URL}/exercicios/automatico")
                end_time = time.time()
                
                if response.status_code == 200:
                    response_time = end_time - start_time
                    response_times.append(response_time)
                    
                    data = response.json()
                    print(f"✅ Exercício: {data['nome']}")
                    print(f"⏱️  Tempo: {response_time:.2f}s")
                    print(f"📝 Descrição: {data['descricao'][:50]}...")
                    print("-" * 40)
                else:
                    print(f"❌ Erro: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Exceção: {str(e)}")
            
            # Pausa entre testes
            await asyncio.sleep(1)
    
    # Estatísticas
    if response_times:
        print("\n📈 ESTATÍSTICAS DE PERFORMANCE")
        print("=" * 60)
        print(f"🎯 Tempo Médio: {statistics.mean(response_times):.2f}s")
        print(f"⚡ Tempo Mínimo: {min(response_times):.2f}s")
        print(f"🐌 Tempo Máximo: {max(response_times):.2f}s")
        print(f"📊 Mediana: {statistics.median(response_times):.2f}s")
        print(f"📈 Desvio Padrão: {statistics.stdev(response_times):.2f}s")
        
        # Avaliação de performance
        avg_time = statistics.mean(response_times)
        if avg_time < 2.0:
            print("🚀 PERFORMANCE: EXCELENTE!")
        elif avg_time < 5.0:
            print("✅ PERFORMANCE: BOA")
        elif avg_time < 10.0:
            print("⚠️  PERFORMANCE: ACEITÁVEL")
        else:
            print("🔴 PERFORMANCE: PRECISA MELHORAR")
    
    return response_times

async def test_cache_performance():
    """Testa a performance do cache"""
    print("\n🗄️  Testando Performance do Cache\n")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Primeiro teste - sem cache
        print("📊 Teste 1: Primeira chamada (sem cache)")
        start_time = time.time()
        
        try:
            response = await client.post(f"{BASE_URL}/exercicios/automatico")
            first_time = time.time() - start_time
            
            if response.status_code == 200:
                exercise_name = response.json()['nome']
                print(f"✅ Exercício: {exercise_name}")
                print(f"⏱️  Tempo sem cache: {first_time:.2f}s")
            
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
            return
        
        # Aguardar um pouco
        await asyncio.sleep(2)
        
        # Segundo teste - pode usar cache
        print("\n📊 Teste 2: Segunda chamada (possível cache)")
        start_time = time.time()
        
        try:
            response = await client.post(f"{BASE_URL}/exercicios/automatico")
            second_time = time.time() - start_time
            
            if response.status_code == 200:
                exercise_name = response.json()['nome']
                print(f"✅ Exercício: {exercise_name}")
                print(f"⏱️  Tempo com possível cache: {second_time:.2f}s")
                
                # Comparação
                improvement = ((first_time - second_time) / first_time) * 100
                if improvement > 0:
                    print(f"🚀 Melhoria: {improvement:.1f}%")
                else:
                    print("📊 Sem melhoria significativa (exercícios diferentes)")
            
        except Exception as e:
            print(f"❌ Erro: {str(e)}")

async def test_cache_status():
    """Verifica status do cache"""
    print("\n🔍 Verificando Status do Cache\n")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"{BASE_URL}/exercicios/cache/status")
            
            if response.status_code == 200:
                data = response.json()
                print(f"📦 Entradas no cache: {data['cache_entries']}")
                print(f"💾 Cache local recente: {data['recent_exercises_cache']}")
                print(f"🎯 Exercícios em cache: {data['cached_exercises']}")
            else:
                print(f"❌ Erro ao verificar cache: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erro: {str(e)}")

async def test_preload():
    """Testa o preload de exercícios"""
    print("\n🔄 Testando Preload de Exercícios\n")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            print("🚀 Iniciando preload...")
            start_time = time.time()
            
            response = await client.post(f"{BASE_URL}/exercicios/preload")
            preload_time = time.time() - start_time
            
            if response.status_code == 200:
                print(f"✅ Preload concluído em {preload_time:.2f}s")
                print(f"📊 Resultado: {response.json()['message']}")
            else:
                print(f"❌ Erro no preload: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erro: {str(e)}")

async def main():
    """Função principal de teste"""
    print("🎯 SUITE DE TESTES DE PERFORMANCE")
    print("🎯 API de Exercícios Otimizada v2.0")
    print("=" * 60)
    
    try:
        # Verificar se API está online
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{BASE_URL}/")
            if response.status_code != 200:
                print("❌ API não está respondendo!")
                return
        
        print("✅ API está online\n")
        
        # Executar testes
        await test_cache_status()
        await test_preload()
        await test_cache_status()  # Verificar após preload
        await test_exercise_generation_performance()
        await test_cache_performance()
        
        print("\n🎉 TESTES CONCLUÍDOS!")
        print("💡 Para melhores resultados, execute novamente após o preload")
        
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 