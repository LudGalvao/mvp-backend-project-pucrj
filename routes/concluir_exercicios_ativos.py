from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from models.exercicios_ativos import Exercicios_ativos
from models.exercicios_historico import Exercicios_historicos
from models.exercicios import Exercicios
from database.session import get_db
from datetime import datetime

router = APIRouter()

@router.patch("/exercicios-ativos/concluidos")
def concluir_exercicios_ativos(id: int, db: Session = Depends(get_db)):
    ativo = db.query(Exercicios_ativos).filter(Exercicios_ativos.id == id, Exercicios_ativos.concluido == False).first()
    if not ativo:
        raise HTTPException(status_code=404, detail="Exercicio ativo não encontrado")
    ativo.concluido = True
    ativo.data_conclusao = datetime.now()
    historico = Exercicios_historicos(
        exercicio_id=ativo.exercicio_id,
        data_inicio=ativo.data_inicio,
        data_conclusao=ativo.data_conclusao
    )
    db.add(historico)
    db.commit()

    novo_exercicio = db.query(Exercicios).order_by(func.random()).first()
    if novo_exercicio:
        novo_ativo = Exercicios_ativos(exercicio_id=novo_exercicio.id)
        db.add(novo_ativo)
        db.commit()
        db.refresh(novo_ativo)
        return {"msg": "Concluído e novo desafio criado", "novo_desafio_id": novo_ativo.id}
    return {"msg": "Concluído, mas não há mais desafios para criar"}