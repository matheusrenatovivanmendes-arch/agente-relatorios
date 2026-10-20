from sqlalchemy import Column,String,Integer,Boolean
from sqlalchemy.orm import declarative_base
import re


Base = declarative_base()


def formatar_cpf(cpf: str) -> str:
    digitos = re.sub(r"\D", "", cpf)
    if len(digitos) != 11:
        raise ValueError("CPF inválido")
    return f"{digitos[:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9:]}"

class Paciente(Base):
    __tablename__ = "pacientes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    cpf = Column(String(14), unique=True, nullable=False)
    idade = Column(Integer, nullable=False)
    diagnostico = Column(String, nullable=False)
    ativo = Column(Boolean, default=True)

    def __init__(self, nome: str, cpf: str, idade: int, diagnostico: str, ativo: bool = True):
        self.nome = nome
        self.cpf = formatar_cpf(cpf)
        self.idade = idade
        self.diagnostico = diagnostico
        self.ativo = ativo