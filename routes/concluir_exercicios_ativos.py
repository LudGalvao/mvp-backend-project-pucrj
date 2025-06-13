from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from models.exercicios import Exercicios
from models.exercicios_historico import Exercicios_historicos
from database.session import get_db
from datetime import datetime
from routes.exercicios import criar_exercicio_automaticamente

router = APIRouter()

@router.patch("/exercicios/concluir/{id}")
async def concluir_exercicio(id: int, db: Session = Depends(get_db)):
    # Busca o exercício ativo
    exercicio = db.query(Exercicios).filter(Exercicios.id == id, Exercicios.exercicio_ativo == True).first()
    if not exercicio:
        raise HTTPException(status_code=404, detail="Exercício ativo não encontrado")
    
    # Marca o exercício como concluído
    exercicio.exercicio_ativo = False
    
    # Registra no histórico
    historico = Exercicios_historicos(
        exercicio_id=exercicio.id,
        data_inicio=datetime.now(),  # Data atual como início
        data_conclusao=datetime.now()  # Data atual como conclusão
    )
    db.add(historico)
    
    # Persiste as mudanças antes de gerar um novo exercício
    db.commit()
    db.refresh(exercicio)
    
    # Gera um novo exercício automaticamente
    try:
        novo_exercicio_gerado = await criar_exercicio_automaticamente(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar novo exercício: {str(e)}")
    
    return {
        "msg": "Exercício concluído e um novo exercício gerado",
        "exercicio_concluido": exercicio.id,
        "novo_exercicio_gerado": novo_exercicio_gerado.id
    }