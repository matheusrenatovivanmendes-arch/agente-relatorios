from pydantic import BaseModel,Field


class PacienteSchema(BaseModel):
    nome: str = Field(max_length=200, min_length=1)
    idade: int = Field(gt=0)
    cpf: str = Field(max_length=11, min_length=11)
    diagnostico: str = Field(min_length=1)

class BuscarPacienteSchema(BaseModel):
    cpf: str = Field(max_length=11, min_length=11)