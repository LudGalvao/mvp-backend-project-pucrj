from pydantic import BaseModel
from datetime import datetime

class ExercicioHistoricoOut(BaseModel):
    id: int
    exercicio_id: int
    data_inicio: datetime
    data_conclusao: datetime

    class Config:
        from_attributes = True