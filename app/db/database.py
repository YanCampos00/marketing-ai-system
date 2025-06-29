from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Define o caminho para o banco de dados SQLite
DATABASE_URL = "sqlite:///./app/db/clients.db"

# Cria o motor do banco de dados
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Cria uma classe base para os modelos declarativos
Base = declarative_base()

# Define o modelo da tabela de clientes
class ClientDB(Base):
    __tablename__ = "clients"

    id = Column(String, primary_key=True, index=True) # ID único do cliente
    nome_exibicao = Column(String, index=True) # Nome para exibição
    contexto_cliente_prompt = Column(Text) # Contexto detalhado para o LLM
    planilha_id_ou_nome = Column(String) # ID ou nome da planilha Google Sheets
    google_sheet_tab_name = Column(String, nullable=True) # Nome da aba Google Ads (opcional)
    meta_sheet_tab_name = Column(String, nullable=True) # Nome da aba Meta Ads (opcional)

# Cria as tabelas no banco de dados (se não existirem)
Base.metadata.create_all(bind=engine)

# Cria uma sessão de banco de dados
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Função para obter uma sessão de banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
