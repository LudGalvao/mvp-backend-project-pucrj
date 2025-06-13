from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.exercicios import Exercicios
from models.exercicios_ativos import Exercicios_ativos
from models.exercicios_historico import Exercicios_historicos
from database.session import get_db

router = APIRouter()

@router.get("/Contador_exercicios")
def contador(db: Session = Depends(get_db)):
    return{
        "total": db.query(Exercicios).count(),
        "ativos": db.query(Exercicios_ativos).count(),
        "concluidos": db.query(Exercicios_historicos).count()
    }