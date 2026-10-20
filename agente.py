import re
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain.agents import create_agent
from schemas.schemas import BuscarPacienteSchema
from pacients import buscar_paciente
from world import texto_evolucao,texto_frequencia,texto_consideracoes,criar_word
from recursos import caminho_recurso

load_dotenv(caminho_recurso(".env"))

llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)

# a ferramenta roda numa thread sem contexto do Streamlit, então não dá pra
# escrever em st.session_state de dentro dela: guardamos aqui e a thread
# principal (render_chat_agente) transfere pra st.session_state depois
_ultimo_relatorio = {"buffer": None, "nome_arquivo": None}


def _nome_arquivo_relatorio(nome_paciente: str) -> str:
    nome_limpo = re.sub(r"[^\w\s-]", "", nome_paciente).strip().replace(" ", "")
    return f"relatorio{nome_limpo}.docx"

@tool
def tool_buscar_paciente(cpf: str) -> str:
    """Busca um paciente pelo CPF e retorna seus dados cadastrais (nome, idade, cpf, diagnóstico)."""
    try:
        dados = BuscarPacienteSchema(cpf=cpf)
        paciente = buscar_paciente(dados)
        return f'Paciente encontrado: nome= {paciente.nome}, idade= {paciente.idade}, cpf={paciente.cpf}, diagnostico= {paciente.diagnostico}'
    except ValueError as e:
        return f"Não consegui buscar o paciente: {e}"

@tool
def tool_texto_diagnostico(cpf: str) -> str:
    """Busca o paciente pelo CPF e retorna só o texto do diagnóstico, pra usar no parágrafo de diagnóstico do relatório."""
    try:
        dados = BuscarPacienteSchema(cpf=cpf)
        paciente = buscar_paciente(dados)
        return paciente.diagnostico
    except ValueError as e:
        return f"Não consegui buscar o diagnóstico: {e}"
@tool
def tool_texto_evolucao(evolucao: str) -> str:
    """Recebe o texto de evolução do paciente ditado pelo usuário e valida pra usar no relatório."""
    try:
        evolucao_final = texto_evolucao(evolucao)
        return evolucao_final
    except ValueError as e:
        return f"Não consegui buscar a evolução: {e}"
@tool
def tool_texto_frequencia(frequencia:str) -> str:
    """Recebe o texto de frequência terapêutica do paciente ditado pelo usuário e valida pra usar no relatório."""
    try:
        frequencia_final = texto_frequencia(frequencia)
        return frequencia_final
    except ValueError as e:
        return f"Não consegui buscar a frequencia: {e}"
@tool
def tool_texto_consideracoes(consideracoes:str) -> str:
    """Recebe o texto de considerações finais do paciente ditado pelo usuário e valida pra usar no relatório."""
    try:
        consideracoes_final = texto_consideracoes(consideracoes)
        return consideracoes_final
    except ValueError as e:
        return f"Não consegui buscar as considerações: {e}"
@tool
def tool_criar_world(cpf: str,evolucao: str,frequencia:str,consideracoes:str) -> str:
    """Monta o relatorio.docx do paciente em memória com os textos de evolução, frequência e considerações."""
    try:
        dados = BuscarPacienteSchema(cpf=cpf)
        paciente = buscar_paciente(dados)
    except ValueError as e:
        return f"Não consegui buscar o paciente: {e}"

    evolucao_final = texto_evolucao(evolucao)
    frequencia_final = texto_frequencia(frequencia)
    consideracoes_final = texto_consideracoes(consideracoes)

    buffer = criar_word(paciente, evolucao_final, frequencia_final, consideracoes_final)
    nome_arquivo = _nome_arquivo_relatorio(paciente.nome)
    _ultimo_relatorio["buffer"] = buffer
    _ultimo_relatorio["nome_arquivo"] = nome_arquivo
    return f"Relatório criado com sucesso em {nome_arquivo}"

def criar_agente():

    ferramentas = [
        tool_buscar_paciente,
        tool_texto_diagnostico,
        tool_texto_evolucao,
        tool_texto_frequencia,
        tool_texto_consideracoes,
        tool_criar_world,
    ]
    return create_agent(
        llm,
        tools=ferramentas,
        system_prompt=(
            "Você é um criador de relatorios fonoaudiologos"
            "voce deve pedir nessa ordem pra criar relatorio: EVOLUÇÃO | FREQUÊNCIA TERAPÊUTICA | CONSIDERAÇÕES FINAIS"
            "Use as ferramentas disponíveis para criar o arquivo word."
            "Se o usuário pedir pra corrigir ou mudar algum dado depois que o relatório já foi criado, "
            "use o valor novo que ele deu, mantenha os outros campos como estavam na conversa, "
            "e gere o relatório de novo com a ferramenta de criar o word (isso sobrescreve o relatório anterior)."
        ),
    )

def render_chat_agente():
    st.title("Assistente de Relatórios")

    # fixa o input de chat embaixo da tela (por padrão, dentro de uma aba
    # ele fica junto do conteúdo em vez de fixo como no chat normal)
    st.markdown(
        """
        <style>
        div[data-testid="stChatInput"] {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            z-index: 999;
            background: var(--background-color, white);
            padding: 1rem 2rem;
            box-shadow: 0 -2px 8px rgba(0,0,0,0.1);
        }
        /* evita que o conteúdo (ex: botão de download) fique escondido atrás do input fixo */
        div[data-testid="stTabPanel"] {
            padding-bottom: 6rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if "agente_chain" not in st.session_state:
        st.session_state["agente_chain"] = criar_agente()
    chain = st.session_state["agente_chain"]

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # exibe as mensagens na tela
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    prompt = st.chat_input()
    if prompt:
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Buscando..."):
                # manda o histórico completo, senão o agente perde o contexto entre mensagens
                resultado = chain.invoke({"messages": st.session_state["messages"]})
                answer = resultado["messages"][-1].content
                st.write(answer)

        st.session_state["messages"].append({"role": "assistant", "content": answer})

        if _ultimo_relatorio["buffer"] is not None:
            st.session_state["relatorio_docx"] = _ultimo_relatorio["buffer"]
            st.session_state["relatorio_nome"] = _ultimo_relatorio["nome_arquivo"]
            _ultimo_relatorio["buffer"] = None
            _ultimo_relatorio["nome_arquivo"] = None

    if "relatorio_docx" in st.session_state:
        st.download_button(
            "Baixar relatório (.docx)",
            data=st.session_state["relatorio_docx"],
            file_name=st.session_state.get("relatorio_nome", "relatorio.docx"),
        )


if __name__ == "__main__":
    render_chat_agente()