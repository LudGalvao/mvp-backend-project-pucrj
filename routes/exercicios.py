from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.exercicios import Exercicios
from schemas.exercicios import ExercicioOut, ExercicioUpdate
from database.session import get_db  
from utils.exercicios_permitidos import EXERCICIOS_PERMITIDOS
from utils.ia import gerar_vantagens_exercicio
import random
from utils.ia import gerar_descricao_exercicio
import asyncio
from typing import List
import time

router = APIRouter()

@router.post("/exercicios/automatico", response_model=ExercicioOut)
async def criar_exercicio_automaticamente(db: Session = Depends(get_db)):
    try:
        tempo_inicio = time.time()
        nome = random.choice(EXERCICIOS_PERMITIDOS)
        
        # Executa as chamadas em paralelo com timeout
        async with asyncio.timeout(30):  # 30 segundos de timeout
            descricao_task = gerar_descricao_exercicio(nome)
            vantagens_task = gerar_vantagens_exercicio(nome, "")
            
            # Aguarda ambas as chamadas
            descricao, vantagens = await asyncio.gather(descricao_task, vantagens_task)
        
        # Atualiza as vantagens com a descrição correta se necessário
        if not vantagens:
            async with asyncio.timeout(30):
                vantagens = await gerar_vantagens_exercicio(nome, descricao)
        
        novo = Exercicios(
            nome=nome,
            descricao=descricao,
            vantagens=vantagens,
            exercicio_ativo=True
        )
        db.add(novo)
        db.commit()
        db.refresh(novo)
        
        tempo_fim = time.time()
        tempo_total = tempo_fim - tempo_inicio
        print(f"Tempo total para gerar exercício: {tempo_total:.2f} segundos")
        
        return novo
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Tempo limite excedido ao gerar exercício")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar exercício: {str(e)}")

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
