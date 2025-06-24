import httpx
from config.settings import OPENROUTER_API_KEY
from functools import lru_cache
import json
import os
import asyncio
from typing import Dict, Any, Optional
import hashlib
import time
from concurrent.futures import ThreadPoolExecutor

# Cache file path
CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database", "db", "exercicios_cache.json")

# Pool de conexões HTTP otimizado
try:
    # Tentar usar HTTP/2 se disponível
    http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(connect=5.0, read=15.0, write=5.0, pool=5.0),
        limits=httpx.Limits(max_keepalive_connections=20, max_connections=50),
        http2=True
    )
except ImportError:
    # Fallback para HTTP/1.1 se h2 não estiver instalado
    http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(connect=5.0, read=15.0, write=5.0, pool=5.0),
        limits=httpx.Limits(max_keepalive_connections=20, max_connections=50)
    )

# Cache em memória global
_exercicios_cache = {}
_cache_loaded = False

# Thread pool para operações de I/O
executor = ThreadPoolExecutor(max_workers=3)

async def load_cache_async() -> Dict[str, Any]:
    """Carrega o cache de forma assíncrona"""
    global _exercicios_cache, _cache_loaded
    
    if _cache_loaded:
        return _exercicios_cache
    
    if os.path.exists(CACHE_FILE):
        loop = asyncio.get_event_loop()
        try:
            def read_cache():
                with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            _exercicios_cache = await loop.run_in_executor(executor, read_cache)
        except Exception as e:
            print(f"Erro ao carregar cache: {e}")
            _exercicios_cache = {}
    else:
        _exercicios_cache = {}
    
    _cache_loaded = True
    return _exercicios_cache

async def save_cache_async(cache: Dict[str, Any]) -> None:
    """Salva o cache de forma assíncrona sem bloquear"""
    loop = asyncio.get_event_loop()
    
    def write_cache():
        try:
            os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erro ao salvar cache: {e}")
    
    # Executar em background sem aguardar
    asyncio.create_task(loop.run_in_executor(executor, write_cache))

@lru_cache(maxsize=500)
def get_cache_key(nome: str, tipo: str) -> str:
    """Gera chave de cache otimizada"""
    return f"{nome.lower()}_{tipo}_{hashlib.md5(nome.encode()).hexdigest()[:8]}"

async def get_cached_value(key: str) -> Optional[str]:
    """Busca valor no cache com carregamento assíncrono"""
    cache = await load_cache_async()
    return cache.get(key)

async def set_cached_value(key: str, value: str) -> None:
    """Define valor no cache"""
    global _exercicios_cache
    cache = await load_cache_async()
    cache[key] = value
    _exercicios_cache = cache
    # Salvar em background
    await save_cache_async(cache)

async def call_ai_api(prompt: str, system_prompt: str, max_tokens: int = 80) -> str:
    """Chamada otimizada para API da IA"""
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Usar modelo mais rápido e eficiente
    data = {
        "model": "microsoft/phi-3-mini-4k-instruct",  # Modelo mais rápido que Mistral
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.3,  # Menor variabilidade para respostas mais consistentes
        "top_p": 0.9,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0
    }
    
    try:
        response = await http_client.post(url, json=data, headers=headers)
        response.raise_for_status()
        resposta = response.json()
        return resposta["choices"][0]["message"]["content"].strip()
    except httpx.TimeoutException:
        # Fallback para modelo ainda mais rápido em caso de timeout
        data["model"] = "openai/gpt-3.5-turbo"
        data["max_tokens"] = min(max_tokens, 60)
        response = await http_client.post(url, json=data, headers=headers)
        response.raise_for_status()
        resposta = response.json()
        return resposta["choices"][0]["message"]["content"].strip()

async def gerar_descricao_exercicio(nome: str) -> str:
    """Gera descrição do exercício com cache otimizado"""
    cache_key = get_cache_key(nome, "descricao")
    
    # Verificar cache primeiro
    cached_value = await get_cached_value(cache_key)
    if cached_value:
        return cached_value

    prompt = f"Descreva '{nome}' em 1-2 linhas simples para iniciantes."
    system_prompt = "Especialista fitness. Respostas concisas e diretas."
    
    resultado = await call_ai_api(prompt, system_prompt, 60)
    
    # Salvar no cache
    await set_cached_value(cache_key, resultado)
    
    return resultado

async def gerar_vantagens_exercicio(nome: str, descricao: str = "") -> str:
    """Gera vantagens do exercício com cache otimizado"""
    cache_key = get_cache_key(nome, "vantagens")
    
    # Verificar cache primeiro
    cached_value = await get_cached_value(cache_key)
    if cached_value:
        return cached_value

    prompt = f"Benefícios de '{nome}' em 1-2 linhas."
    system_prompt = "Personal trainer. Foque nos principais benefícios."
    
    resultado = await call_ai_api(prompt, system_prompt, 50)
    
    # Salvar no cache
    await set_cached_value(cache_key, resultado)
    
    return resultado

async def gerar_passo_a_passo_exercicio(nome: str) -> str:
    """Gera passo a passo do exercício com cache otimizado"""
    cache_key = get_cache_key(nome, "passo_a_passo")
    
    # Verificar cache primeiro
    cached_value = await get_cached_value(cache_key)
    if cached_value:
        return cached_value

    prompt = f"3 etapas simples para '{nome}'. Format: 1. ... 2. ... 3. ..."
    system_prompt = "Instrutor fitness. Passos numerados e concisos."
    
    resultado = await call_ai_api(prompt, system_prompt, 90)
    
    # Salvar no cache
    await set_cached_value(cache_key, resultado)
    
    return resultado

# Função para pré-carregar cache dos exercícios mais comuns
async def preload_common_exercises():
    """Pré-carrega exercícios populares no cache"""
    common_exercises = [
        "Polichinelo", "Agachamento livre", "Prancha", 
        "Flexão de braço", "Abdominal", "Caminhada"
    ]
    
    tasks = []
    for exercise in common_exercises:
        cache_key_desc = get_cache_key(exercise, "descricao")
        cache_key_vant = get_cache_key(exercise, "vantagens")
        cache_key_passo = get_cache_key(exercise, "passo_a_passo")
        
        # Verificar se já estão em cache
        cache = await load_cache_async()
        if not cache.get(cache_key_desc):
            tasks.append(gerar_descricao_exercicio(exercise))
        if not cache.get(cache_key_vant):
            tasks.append(gerar_vantagens_exercicio(exercise))
        if not cache.get(cache_key_passo):
            tasks.append(gerar_passo_a_passo_exercicio(exercise))
    
    if tasks:
        try:
            await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            print(f"Erro no preload: {e}")

# Função para gerar exercício completo otimizada
async def gerar_exercicio_completo_otimizado(nome: str) -> Dict[str, str]:
    """
    Gera exercício completo com máxima otimização:
    1. Verifica cache primeiro
    2. Executa em paralelo se necessário
    3. Usa timeout agressivo
    4. Fallback para dados básicos se necessário
    """
    
    # Verificar se tudo já está em cache
    cache_key_desc = get_cache_key(nome, "descricao")
    cache_key_vant = get_cache_key(nome, "vantagens")
    cache_key_passo = get_cache_key(nome, "passo_a_passo")
    
    cache = await load_cache_async()
    descricao = cache.get(cache_key_desc)
    vantagens = cache.get(cache_key_vant)
    passo_a_passo = cache.get(cache_key_passo)
    
    # Se tudo está em cache, retorna imediatamente
    if descricao and vantagens and passo_a_passo:
        return {
            "descricao": descricao,
            "vantagens": vantagens,
            "passo_a_passo": passo_a_passo
        }
    
    # Preparar tasks apenas para o que não está em cache
    tasks = []
    if not descricao:
        tasks.append(("descricao", gerar_descricao_exercicio(nome)))
    if not vantagens:
        tasks.append(("vantagens", gerar_vantagens_exercicio(nome)))
    if not passo_a_passo:
        tasks.append(("passo_a_passo", gerar_passo_a_passo_exercicio(nome)))
    
    # Executar em paralelo com timeout agressivo
    if tasks:
        try:
            async with asyncio.timeout(8.0):  # 8 segundos no máximo
                results = await asyncio.gather(*[task[1] for task in tasks])
                
                # Mapear resultados
                for i, (campo, _) in enumerate(tasks):
                    if campo == "descricao" and not descricao:
                        descricao = results[i]
                    elif campo == "vantagens" and not vantagens:
                        vantagens = results[i]
                    elif campo == "passo_a_passo" and not passo_a_passo:
                        passo_a_passo = results[i]
                        
        except asyncio.TimeoutError:
            print(f"Timeout na geração de {nome}, usando fallbacks")
            # Fallbacks básicos se houver timeout
            if not descricao:
                descricao = f"Exercício {nome} para fortalecimento e condicionamento físico."
            if not vantagens:
                vantagens = "Melhora força, resistência e saúde geral."
            if not passo_a_passo:
                passo_a_passo = "1. Posicione-se corretamente. 2. Execute o movimento. 3. Repita conforme orientação."
    
    return {
        "descricao": descricao or f"Exercício {nome}",
        "vantagens": vantagens or "Benefícios para saúde e fitness",
        "passo_a_passo": passo_a_passo or "Siga orientação de profissional"
    }

async def cleanup():
    """Limpa recursos ao encerrar"""
    await http_client.aclose()
    executor.shutdown(wait=True)