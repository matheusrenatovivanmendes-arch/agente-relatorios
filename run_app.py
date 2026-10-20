import os
import sys


def main():
    # roda com o diretório de trabalho sendo a pasta do executável, pra o
    # banco de dados (meubanco.db) ficar sempre do lado do .exe
    pasta_base = os.path.dirname(sys.executable if getattr(sys, "frozen", False) else os.path.abspath(__file__))
    os.chdir(pasta_base)

    from recursos import caminho_recurso
    from streamlit.web import cli as stcli

    sys.argv = [
        "streamlit",
        "run",
        caminho_recurso("app.py"),
        "--global.developmentMode=false",
        "--server.headless=false",
    ]
    sys.exit(stcli.main())


if __name__ == "__main__":
    main()
