from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.exercicios import Exercicios
from schemas.exercicios import ExercicioOut, ExercicioCreate, ExercicioUpdate
from database.session import get_db  

router = APIRouter()

@router.post("/exercicios", response_model=ExercicioOut)
def criar_exercicio(exercicio: ExercicioCreate, db: Session = Depends(get_db)):
    novo = Exercicios(**exercicio.model_dump())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo

@router.put("/exercicios", response_model=ExercicioOut)
def atualizar_exercicio(id: int, exercicio: ExercicioUpdate, db: Session = Depends(get_db)):
    obj = db.query(Exercicios).filter(Exercicios.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Exercício não encontrado")
    for k, v in exercicio.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj
