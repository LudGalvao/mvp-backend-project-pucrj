import httpx
from config.settings import OPENROUTER_API_KEY
from functools import lru_cache
import json
import os
from typing import Dict, Any

# Cache file path
CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database", "db", "exercicios_cache.json")

# Cliente HTTP persistente
http_client = httpx.AsyncClient(timeout=10.0)

def load_cache() -> Dict[str, Any]:
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_cache(cache: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

# Cache em memória com LRU
@lru_cache(maxsize=100)
def get_cached_value(key: str) -> str:
    return _exercicios_cache.get(key, "")

# Cache em memória
_exercicios_cache = load_cache()

async def gerar_vantagens_exercicio(nome: str, descricao: str) -> str:
    # Verifica cache
    cache_key = f"{nome}_vantagens"
    cached_value = get_cached_value(cache_key)
    if cached_value:
        return cached_value

    prompt = f"Benefícios do exercício '{nome}' em 2 linhas."
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "mistralai/mistral-nemo",
        "messages": [
            {"role": "system", "content": "Especialista em educação física. Respostas curtas e objetivas."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 100  # Limita o tamanho da resposta
    }
    
    response = await http_client.post(url, json=data, headers=headers)
    response.raise_for_status()
    resposta = response.json()
    resultado = resposta["choices"][0]["message"]["content"].strip()
    
    # Salva no cache
    _exercicios_cache[cache_key] = resultado
    save_cache(_exercicios_cache)
    
    return resultado
    
async def gerar_descricao_exercicio(nome: str) -> str:
    # Verifica cache
    cache_key = f"{nome}_descricao"
    cached_value = get_cached_value(cache_key)
    if cached_value:
        return cached_value

    prompt = f"Descreva o exercício '{nome}' em 2 linhas para iniciantes."
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "mistralai/mistral-nemo",
        "messages": [
            {"role": "system", "content": "Especialista em educação física. Respostas curtas e objetivas."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 100  # Limita o tamanho da resposta
    }
    
    response = await http_client.post(url, json=data, headers=headers)
    response.raise_for_status()
    resposta = response.json()
    resultado = resposta["choices"][0]["message"]["content"].strip()
    
    # Salva no cache
    _exercicios_cache[cache_key] = resultado
    save_cache(_exercicios_cache)
    
    return resultado