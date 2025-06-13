from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from models.exercicios import Exercicios
from models.exercicios_historico import Exercicios_historicos
from database.session import get_db
from datetime import datetime

router = APIRouter()

@router.patch("/exercicios/concluir/{id}")
def concluir_exercicio(id: int, db: Session = Depends(get_db)):
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
    
    # Busca um novo exercício aleatório que não esteja ativo
    novo_exercicio = db.query(Exercicios).filter(
        Exercicios.exercicio_ativo == False,
        Exercicios.id != id  # Evita selecionar o mesmo exercício
    ).order_by(func.random()).first()
    
    if novo_exercicio:
        # Marca o novo exercício como ativo
        novo_exercicio.exercicio_ativo = True
        db.commit()
        return {
            "msg": "Exercício concluído e novo exercício ativado",
            "exercicio_concluido": exercicio.id,
            "novo_exercicio": novo_exercicio.id
        }
    
    db.commit()
    return {
        "msg": "Exercício concluído",
        "exercicio_concluido": exercicio.id
    }