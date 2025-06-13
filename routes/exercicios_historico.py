from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.exercicios_historico import Exercicios_historicos
from models.exercicios import Exercicios
from database.session import get_db
from schemas.exercicios_historico import ExercicioHistoricoOut
from typing import List
from sqlalchemy import select

router = APIRouter()

@router.get("/historico/exercicios/detalhado")
def listar_exercicios_detalhado(db: Session = Depends(get_db)):
    # Busca todos os exercícios com seus históricos
    exercicios = db.query(Exercicios).all()
    
    resultado = []
    for exercicio in exercicios:
        # Busca o histórico deste exercício
        historicos = db.query(Exercicios_historicos).filter(
            Exercicios_historicos.exercicio_id == exercicio.id
        ).all()
        
        # Formata as datas do histórico
        historicos_formatados = []
        for hist in historicos:
            historicos_formatados.append({
                "data_inicio": hist.data_inicio.strftime("%d/%m/%Y %H:%M:%S") if hist.data_inicio else None,
                "data_conclusao": hist.data_conclusao.strftime("%d/%m/%Y %H:%M:%S") if hist.data_conclusao else None
            })
        
        # Adiciona o exercício com seu histórico ao resultado
        resultado.append({
            "id": exercicio.id,
            "nome": exercicio.nome,
            "descricao": exercicio.descricao,
            "vantagens": exercicio.vantagens,
            "exercicio_ativo": exercicio.exercicio_ativo,
            "historico": historicos_formatados,
            "total_concluido": len(historicos_formatados)
        })
    
    return resultado
