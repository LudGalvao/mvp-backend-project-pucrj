from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.exercicios_historico import Exercicios_historicos
from database.session import get_db
from schemas.exercicios_historico import ExercicioHistoricoOut

router = APIRouter()

@router.get("/Historico_exercicios", response_model=list[ExercicioHistoricoOut])
def listar_historico(db: Session = Depends(get_db)):
    return db.query(Exercicios_historicos).all()
