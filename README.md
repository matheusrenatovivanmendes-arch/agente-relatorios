#  Agente de Relatórios Fonoaudiológicos

Sistema que automatiza a criação de relatórios clínicos em Word (.docx) a partir de uma conversa em linguagem natural com um agente de IA. Feito originalmente para uso real em um consultório de fonoaudiologia, cobrindo todo o fluxo: cadastro de pacientes, coleta dos dados do relatório via chat, e geração do documento formatado — sem precisar editar Word manualmente.

## Como funciona

1. O profissional cadastra o paciente (nome, idade, CPF, diagnóstico) numa interface Streamlit.
2. Na aba do assistente, ele conversa naturalmente com o agente contando a evolução, frequência terapêutica e considerações finais do paciente.
3. Um agente LangChain (rodando um modelo via Groq) usa ferramentas (`tools`) para buscar o paciente no banco, validar cada parte do relato, e montar o relatório.
4. O relatório é gerado em memória como um `.docx` (logo, dados do paciente, texto formatado, assinatura) e fica disponível direto pra download — nada é salvo em disco além do banco de dados local.

## Stack

- **Streamlit** — interface web
- **LangChain + LangGraph + Groq** — agente de IA com tool-calling
- **SQLAlchemy + SQLite** — persistência dos pacientes
- **python-docx** — geração do relatório em Word
- **Pydantic** — validação de dados
- **PyInstaller + GitHub Actions** — empacotamento como executável standalone (Windows/Linux), pra uso sem precisar instalar Python

## Rodando localmente

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copie `.env_example` para `.env` e preencha:

```
DATABASE_URL=sqlite:///meubanco.db
GROQ_API_KEY=sua_chave_aqui
```

Adicione sua logo e assinatura em `imagem/logo.png` e `imagem/assinatura.png` (não versionados, por serem dados específicos de cada profissional).

```bash
streamlit run app.py
```

## Empacotando como executável

O workflow do GitHub Actions (`.github/workflows/build.yml`, não incluído neste repositório público) builda um executável único via PyInstaller, tanto pra Windows quanto Linux, usando `run_app.py` como ponto de entrada — permitindo que alguém sem conhecimento técnico use o sistema com um duplo clique.

## Estrutura

```
models.py          # modelos SQLAlchemy (Paciente) + validação/formatação de CPF
schemas/            # schemas Pydantic de entrada
extensions.py       # conexão com o banco
pacients.py          # CRUD de pacientes
world.py             # geração do relatório Word
agente.py            # ferramentas do agente e orquestração LangChain
app.py               # interface Streamlit
run_app.py           # launcher usado no empacotamento
```

## Sobre dados pessoais

Este é um sistema de uso local e individual — os dados dos pacientes ficam só no SQLite local de quem roda o programa, sem sincronização externa. O texto do relato (incluindo CPF e diagnóstico, usados pelo agente pra localizar o paciente) é enviado ao provedor de IA (Groq) durante a geração do relatório, como em qualquer integração com LLM via API.
