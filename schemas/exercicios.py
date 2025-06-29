from pydantic import BaseModel

class ExercicioBase(BaseModel):
    nome: str
    descricao: str
    vantagens: str
    passo_a_passo: str | None = None
    exercicio_ativo: bool = False

class ExercicioCreate(ExercicioBase):
    pass

class ExercicioUpdate(BaseModel):
    nome: str | None = None
    descricao: str | None = None
    vantagens: str | None = None
    passo_a_passo: str | None = None
    exercicio_ativo: bool | None = None

class ExercicioOut(ExercicioBase):
    id: int

    class Config:
        from_attributes = True