from models import Paciente, formatar_cpf
from sqlalchemy.exc import SQLAlchemyError
from schemas.schemas import PacienteSchema,BuscarPacienteSchema
from extensions import session


def criar_paciente(dados: PacienteSchema):
    try:
        paciente = Paciente(nome=dados.nome,idade=dados.idade,cpf=dados.cpf,diagnostico=dados.diagnostico)
        session.add(paciente)
        session.commit()
        return paciente
    except SQLAlchemyError as e:
        session.rollback()
        raise e

def atualizar_paciente(dados: BuscarPacienteSchema, idade_nova: int = None, diagnostico_novo: str = None):
    paciente = session.query(Paciente).filter_by(cpf=formatar_cpf(dados.cpf)).first()
    if not paciente:
        return 'Paciente nao existe'
    if idade_nova is not None:
        paciente.idade = idade_nova
    if diagnostico_novo is not None:
        paciente.diagnostico = diagnostico_novo
    session.commit()
    return paciente

def deletar_paciente(dados:BuscarPacienteSchema):
    paciente = session.query(Paciente).filter_by(cpf=formatar_cpf(dados.cpf)).first()
    if not paciente:
        return 'Paciente nao existe'
    session.delete(paciente)
    session.commit()
    return 'deu boa'

def buscar_paciente(dados: BuscarPacienteSchema):
    paciente = session.query(Paciente).filter_by(cpf=formatar_cpf(dados.cpf)).first()
    if not paciente:
       raise ValueError('Paciente nao existe')
    return paciente

def todos_pacientes():
    pacientes = session.query(Paciente).all()
    resultados = []
    for p in pacientes:
        resultados.append({
            'id': p.id,
            'nome': p.nome,
            'cpf': p.cpf,
            'idade': p.idade,
            'diagnostico': p.diagnostico
        })
    return resultados

