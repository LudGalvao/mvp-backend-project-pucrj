import httpx
from config.settings import OPENROUTER_API_KEY
from functools import lru_cache
import json
import os

# Cache file path
CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database", "db", "exercicios_cache.json")

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

# Cache em memória
_exercicios_cache = load_cache()

async def gerar_vantagens_exercicio(nome, descricao):
    # Verifica cache
    cache_key = f"{nome}_vantagens"
    if cache_key in _exercicios_cache:
        return _exercicios_cache[cache_key]

    prompt = f"Benefícios de praticar o exercício '{nome}'? Descrição: {descricao}. Responda de forma curta, bastante clara e objetiva(No max 3 linhas de )."
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "Você é um especialista em educação física."},
            {"role": "user", "content": prompt}
        ]
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data, headers=headers)
        response.raise_for_status()
        resposta = response.json()
        resultado = resposta["choices"][0]["message"]["content"]
        
        # Salva no cache
        _exercicios_cache[cache_key] = resultado
        save_cache(_exercicios_cache)
        
        return resultado
    
async def gerar_descricao_exercicio(nome):
    # Verifica cache
    cache_key = f"{nome}_descricao"
    if cache_key in _exercicios_cache:
        return _exercicios_cache[cache_key]

    prompt = f"Descreva brevemente o exercício '{nome}' de forma clara e concisa para iniciantes."
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "Você é um especialista em educação física."},
            {"role": "user", "content": prompt}
        ]
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data, headers=headers)
        response.raise_for_status()
        resposta = response.json()
        resultado = resposta["choices"][0]["message"]["content"]
        
        # Salva no cache
        _exercicios_cache[cache_key] = resultado
        save_cache(_exercicios_cache)
        
        return resultado