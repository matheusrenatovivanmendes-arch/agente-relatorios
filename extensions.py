import os
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from sqlalchemy import create_engine
from models import Base
from recursos import caminho_recurso
load_dotenv(caminho_recurso(".env"))

db = create_engine(os.getenv("DATABASE_URL", "sqlite:///meubanco.db"))
Base.metadata.create_all(db)
Session = sessionmaker(bind=db)
session = Session()