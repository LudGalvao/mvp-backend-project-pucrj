from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.exercicios import Exercicios
from schemas.exercicios import ExercicioOut, ExercicioUpdate
from database.session import get_db  
from utils.exercicios_permitidos import EXERCICIOS_PERMITIDOS
from utils.ia import gerar_exercicio_completo_otimizado, preload_common_exercises
import random
import asyncio
from typing import List
import time

router = APIRouter()

# Cache local para exercícios recém criados (evita recrear os mesmos)
_recent_exercises_cache = {}
_last_exercise_name = None

@router.post("/exercicios/automatico", response_model=ExercicioOut)
async def criar_exercicio_automaticamente(db: Session = Depends(get_db)):
    """
    Cria exercício automaticamente com máxima otimização:
    1. Evita repetir o último exercício
    2. Usa cache inteligente
    3. Execução em paralelo quando necessário
    4. Timeout agressivo com fallbacks
    """
    global _last_exercise_name
    
    try:
        tempo_inicio = time.time()
        
        # Selecionar exercício diferente do último
        available_exercises = [e for e in EXERCICIOS_PERMITIDOS if e != _last_exercise_name]
        nome = random.choice(available_exercises)
        _last_exercise_name = nome
        
        print(f"Gerando exercício: {nome}")
        
        # Verificar se exercício já existe no cache local recente
        cache_key = f"exercise_{nome.lower().replace(' ', '_')}"
        if cache_key in _recent_exercises_cache:
            cached_exercise = _recent_exercises_cache[cache_key]
            print(f"Usando cache local para {nome}")
            
            # Criar novo registro no DB
            novo = Exercicios(
                nome=nome,
                descricao=cached_exercise["descricao"],
                vantagens=cached_exercise["vantagens"],
                passo_a_passo=cached_exercise["passo_a_passo"],
                exercicio_ativo=True
            )
            db.add(novo)
            db.commit()
            db.refresh(novo)
            
            tempo_fim = time.time()
            print(f"Exercício criado do cache em {tempo_fim - tempo_inicio:.2f}s")
            return novo
        
        # Gerar exercício com função otimizada
        try:
            resultado = await gerar_exercicio_completo_otimizado(nome)
        except Exception as e:
            print(f"Erro na geração otimizada: {e}")
            # Fallback para dados básicos
            resultado = {
                "descricao": f"Exercício {nome} para fortalecimento muscular e condicionamento físico.",
                "vantagens": "Melhora força, resistência, coordenação e saúde cardiovascular.",
                "passo_a_passo": "1. Posicione-se adequadamente. 2. Execute o movimento com controle. 3. Mantenha respiração constante."
            }
        
        # Salvar no cache local para uso futuro
        _recent_exercises_cache[cache_key] = resultado
        
        # Limitar tamanho do cache local
        if len(_recent_exercises_cache) > 20:
            # Remove o mais antigo
            oldest_key = next(iter(_recent_exercises_cache))
            del _recent_exercises_cache[oldest_key]
        
        # Criar exercício no banco
        novo = Exercicios(
            nome=nome,
            descricao=resultado["descricao"],
            vantagens=resultado["vantagens"],
            passo_a_passo=resultado["passo_a_passo"],
            exercicio_ativo=True
        )
        db.add(novo)
        db.commit()
        db.refresh(novo)
        
        tempo_fim = time.time()
        tempo_total = tempo_fim - tempo_inicio
        print(f"Exercício '{nome}' criado em {tempo_total:.2f} segundos")
        
        return novo
        
    except Exception as e:
        db.rollback()
        print(f"Erro ao criar exercício: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao criar exercício: {str(e)}")

@router.post("/exercicios/preload")
async def preload_exercises():
    """
    Endpoint para pré-carregar exercícios populares no cache.
    Útil para melhorar performance após deploy.
    """
    try:
        await preload_common_exercises()
        return {"message": "Exercícios populares pré-carregados com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no preload: {str(e)}")

@router.get("/exercicios/cache/status")
async def get_cache_status():
    """
    Retorna status do cache para monitoramento
    """
    from utils.ia import load_cache_async
    
    try:
        cache = await load_cache_async()
        return {
            "cache_entries": len(cache),
            "recent_exercises_cache": len(_recent_exercises_cache),
            "cached_exercises": list(_recent_exercises_cache.keys())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao verificar cache: {str(e)}")

@router.put("/update/exercicios", response_model=ExercicioOut)
def atualizar_exercicio(id: int, exercicio: ExercicioUpdate, db: Session = Depends(get_db)):
    try:
        obj = db.query(Exercicios).filter(Exercicios.id == id).first()
        if not obj:
            raise HTTPException(status_code=404, detail="Exercício não encontrado")
        for k, v in exercicio.model_dump(exclude_unset=True).items():
            setattr(obj, k, v)
        db.commit()
        db.refresh(obj)
        return obj
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar exercício: {str(e)}")

@router.get("/exercicios_permitidos")
def listar_exercicios_permitidos():
    return EXERCICIOS_PERMITIDOS

@router.get("/exercicios/{id}", response_model=ExercicioOut)
def get_exercicio(id: int, db: Session = Depends(get_db)):
    obj = db.query(Exercicios).filter(Exercicios.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Exercício não encontrado")
    return obj

# Função para inicializar preload em background (executar no startup)
async def startup_preload():
    """
    Executa preload em background no startup da aplicação
    """
    try:
        print("Iniciando preload de exercícios...")
        await preload_common_exercises()
        print("Preload concluído com sucesso!")
    except Exception as e:
        print(f"Erro no preload de startup: {e}")

# Adicionar cleanup de cache periódico
import threading
import time as time_module

def periodic_cache_cleanup():
    """
    Limpa cache periodicamente para evitar crescimento excessivo
    """
    global _recent_exercises_cache
    
    while True:
        time_module.sleep(3600)  # A cada hora
        if len(_recent_exercises_cache) > 15:
            # Manter apenas os 10 mais recentes
            keys_to_keep = list(_recent_exercises_cache.keys())[-10:]
            _recent_exercises_cache = {k: _recent_exercises_cache[k] for k in keys_to_keep}
            print("Cache local limpo automaticamente")

# Iniciar thread de limpeza
cleanup_thread = threading.Thread(target=periodic_cache_cleanup, daemon=True)
cleanup_thread.start()
