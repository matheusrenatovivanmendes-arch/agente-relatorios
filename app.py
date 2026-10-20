import streamlit as st
from pydantic import ValidationError

from pacients import criar_paciente, buscar_paciente, atualizar_paciente, deletar_paciente, todos_pacientes
from schemas.schemas import PacienteSchema, BuscarPacienteSchema
from agente import render_chat_agente

st.title("Gestão de Pacientes")

aba_cadastrar, aba_listar, aba_buscar, aba_atualizar, aba_deletar, aba_agente = st.tabs(
    ["Cadastrar", "Listar", "Buscar", "Atualizar", "Deletar", "Relatório (Agente)"]
)

with aba_cadastrar:
    with st.form("form_cadastrar"):
        nome = st.text_input("Nome")
        idade = st.number_input("Idade", min_value=1, step=1)
        cpf = st.text_input("CPF (somente números)", max_chars=11)
        diagnostico = st.text_input("Diagnóstico")
        enviado = st.form_submit_button("Cadastrar paciente")

    if enviado:
        try:
            dados = PacienteSchema(nome=nome, idade=idade, cpf=cpf, diagnostico=diagnostico)
            paciente = criar_paciente(dados)
            st.success(f"Paciente {paciente.nome} cadastrado com sucesso.")
        except ValidationError as e:
            st.error(f"Dados inválidos: {e}")
        except Exception as e:
            st.error(f"Erro ao cadastrar: {e}")

with aba_listar:
    pacientes = todos_pacientes()
    if pacientes:
        st.dataframe(pacientes, width='stretch')
    else:
        st.info("Nenhum paciente cadastrado ainda.")

with aba_buscar:
    cpf_busca = st.text_input("CPF do paciente (somente números)", max_chars=11, key="cpf_buscar")
    if st.button("Buscar paciente"):
        try:
            dados = BuscarPacienteSchema(cpf=cpf_busca)
            paciente = buscar_paciente(dados)
            st.write(f"**Nome:** {paciente.nome}")
            st.write(f"**CPF:** {paciente.cpf}")
            st.write(f"**Idade:** {paciente.idade}")
            st.write(f"**Diagnóstico:** {paciente.diagnostico}")
        except ValidationError as e:
            st.error(f"CPF inválido: {e}")
        except ValueError as e:
            st.error(str(e))

with aba_atualizar:
    cpf_atualizar = st.text_input("CPF do paciente (somente números)", max_chars=11, key="cpf_atualizar")
    idade_nova = st.number_input("Nova idade (deixe 0 pra não alterar)", min_value=0, step=1, key="idade_atualizar")
    diagnostico_novo = st.text_input("Novo diagnóstico (deixe vazio pra não alterar)", key="diagnostico_atualizar")
    if st.button("Atualizar paciente"):
        try:
            dados = BuscarPacienteSchema(cpf=cpf_atualizar)
            resultado = atualizar_paciente(
                dados=dados,
                idade_nova=idade_nova if idade_nova > 0 else None,
                diagnostico_novo=diagnostico_novo if diagnostico_novo.strip() else None,
            )
            if isinstance(resultado, str):
                st.error(resultado)
            else:
                st.success(f"Paciente {resultado.nome} atualizado com sucesso.")
        except ValidationError as e:
            st.error(f"CPF inválido: {e}")

with aba_deletar:
    cpf_deletar = st.text_input("CPF do paciente (somente números)", max_chars=11, key="cpf_deletar")
    if st.button("Deletar paciente"):
        try:
            dados = BuscarPacienteSchema(cpf=cpf_deletar)
            resultado = deletar_paciente(dados)
            if resultado == "deu boa":
                st.success("Paciente deletado com sucesso.")
            else:
                st.error(resultado)
        except ValidationError as e:
            st.error(f"CPF inválido: {e}")

with aba_agente:
    render_chat_agente()
