from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Define o caminho para o banco de dados SQLite a partir de uma variável de ambiente, com um padrão
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app/db/clients.db")

# Cria o motor do banco de dados
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} # Necessário apenas para SQLite
)

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

class PromptDB(Base):
    __tablename__ = "prompts"

    id = Column(String, primary_key=True, index=True) # ID único do prompt
    nome = Column(String, unique=True, index=True) # Nome do prompt (ex: consolidated_report)
    conteudo = Column(Text) # Conteúdo do prompt
    descricao = Column(String, nullable=True) # Descrição do prompt (opcional)

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


# --- Funções CRUD (Create, Read, Update, Delete) ---

def get_client(db: sessionmaker, client_id: str):
    return db.query(ClientDB).filter(ClientDB.id == client_id).first()

def get_clients(db: sessionmaker):
    return db.query(ClientDB).all()

def create_client(db: sessionmaker, client: ClientDB):
    db.add(client)
    db.commit()
    db.refresh(client)
    return client

def update_client(db: sessionmaker, client_id: str, client_data: dict):
    db_client = get_client(db, client_id)
    if db_client:
        for key, value in client_data.items():
            setattr(db_client, key, value)
        db.commit()
        db.refresh(db_client)
    return db_client

def delete_client(db: sessionmaker, client_id: str):
    db_client = get_client(db, client_id)
    if db_client:
        db.delete(db_client)
        db.commit()
    return db_client
