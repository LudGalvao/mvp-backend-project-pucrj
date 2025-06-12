from pydantic import BaseModel

class ExercicioBase(BaseModel):
    nome: str
    descricao: str
    vantagens: str

class ExercicioCreate(ExercicioBase):
    pass

class ExercicioUpdate(BaseModel):
    nome: str | None = None
    descricao: str | None = None
    vantagens: str | None = None

class ExercicioOut(ExercicioBase):
    id: int

    class Config:
        orm_mode = True