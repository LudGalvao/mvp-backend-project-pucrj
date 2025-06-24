# Configurações de Performance para Otimização da IA

# Configurações de Cache
CACHE_CONFIG = {
    "max_memory_cache_size": 500,  # Máximo de itens no cache em memória
    "cache_ttl_hours": 24,  # Tempo de vida do cache em horas
    "preload_popular_exercises": True,  # Pré-carregar exercícios populares
    "auto_cleanup_interval_hours": 1,  # Limpeza automática do cache
}

# Configurações de IA
AI_CONFIG = {
    "primary_model": "microsoft/phi-3-mini-4k-instruct",  # Modelo principal (mais rápido)
    "fallback_model": "openai/gpt-3.5-turbo",  # Modelo de fallback
    "max_tokens_description": 60,
    "max_tokens_benefits": 50,
    "max_tokens_steps": 90,
    "temperature": 0.3,  # Menor variabilidade
    "timeout_seconds": 8,  # Timeout agressivo
    "max_retries": 2,
}

# Configurações de HTTP
HTTP_CONFIG = {
    "connect_timeout": 5.0,
    "read_timeout": 15.0,
    "write_timeout": 5.0,
    "pool_timeout": 5.0,
    "max_keepalive_connections": 20,
    "max_connections": 50,
    "enable_http2": True,
}

# Exercícios prioritários para preload
PRIORITY_EXERCISES = [
    "Polichinelo",
    "Agachamento livre", 
    "Prancha",
    "Flexão de braço",
    "Abdominal",
    "Caminhada",
    "Alongamento",
    "Afundo",
    "Mountain climber",
    "Burpee"
]

# Fallbacks para exercícios
EXERCISE_FALLBACKS = {
    "description_template": "Exercício {name} para fortalecimento muscular e condicionamento físico.",
    "benefits_template": "Melhora força, resistência, coordenação e saúde cardiovascular.",
    "steps_template": "1. Posicione-se adequadamente. 2. Execute o movimento com controle. 3. Mantenha respiração constante."
}

# Configurações de monitoramento
MONITORING_CONFIG = {
    "log_response_times": True,
    "log_cache_hits": True,
    "log_ai_errors": True,
    "performance_threshold_ms": 5000,  # Alertar se > 5 segundos
} 