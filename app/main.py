from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import date
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

from app.agents.orchestrator import Orchestrator, get_orchestrator
from app.db.database import get_db, engine, Base, ClientDB
from app.agents.media_agent import METRICAS_DISPONIVEIS

# Cria as tabelas no banco de dados (se não existirem)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Marketing AI System API", version="1.1.0")

# Configuração de CORS
origins = [
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Modelos Pydantic (DTOs) ---
class ClientBase(BaseModel):
    nome_exibicao: str
    contexto_cliente_prompt: str
    planilha_id_ou_nome: str
    google_sheet_tab_name: Optional[str] = None
    meta_sheet_tab_name: Optional[str] = None

class ClientCreate(ClientBase):
    id: str

class ClientUpdate(ClientBase):
    nome_exibicao: Optional[str] = None
    contexto_cliente_prompt: Optional[str] = None
    planilha_id_ou_nome: Optional[str] = None

class ClientInDB(ClientBase):
    id: str
    class Config:
        from_attributes = True

class AnalysisRequest(BaseModel):
    client_id: str
    mes_analise: date
    metricas_selecionadas: List[str] = []

# --- Endpoints da API ---

@app.on_event("startup")
async def startup_event():
    """
    Carrega o Orchestrator na inicialização para reutilização.
    """
    app.state.orchestrator = get_orchestrator()

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Marketing AI System v1! Visit /docs for API documentation."}

@app.get("/metrics")
async def get_available_metrics():
    base_metrics = ["Spend", "Revenue", "Sessions", "Conversions", "Clicks", "Impressions"]
    all_metrics = list(METRICAS_DISPONIVEIS.keys()) + base_metrics
    return sorted(list(set(all_metrics)))

@app.get("/clients", response_model=Dict[str, ClientInDB])
async def get_clients(db: Session = Depends(get_db)):
    clients_db = db.query(ClientDB).all()
    return {client.id: ClientInDB.from_orm(client) for client in clients_db}

@app.post("/clients", response_model=ClientInDB)
async def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    db_client = db.query(ClientDB).filter(ClientDB.id == client.id).first()
    if db_client:
        raise HTTPException(status_code=400, detail=f"Cliente com ID '{client.id}' já existe.")
    db_client = ClientDB(**client.dict())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

@app.put("/clients/{client_id}", response_model=ClientInDB)
async def update_client(client_id: str, client_data: ClientUpdate, db: Session = Depends(get_db)):
    db_client = db.query(ClientDB).filter(ClientDB.id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail=f"Cliente com ID '{client_id}' não encontrado.")
    for key, value in client_data.dict(exclude_unset=True).items():
        setattr(db_client, key, value)
    db.commit()
    db.refresh(db_client)
    return db_client

@app.delete("/clients/{client_id}")
async def delete_client(client_id: str, db: Session = Depends(get_db)):
    db_client = db.query(ClientDB).filter(ClientDB.id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail=f"Cliente com ID '{client_id}' não encontrado.")
    db.delete(db_client)
    db.commit()
    return {"message": f"Cliente '{client_id}' removido com sucesso.", "client_id": client_id}

@app.post("/analyze")
async def run_analysis(request: AnalysisRequest, db: Session = Depends(get_db)):
    orchestrator: Orchestrator = app.state.orchestrator
    client_config_db = db.query(ClientDB).filter(ClientDB.id == request.client_id).first()
    if not client_config_db:
        raise HTTPException(status_code=404, detail=f"Cliente com ID '{request.client_id}' não encontrado.")

    client_config_dict = ClientInDB.from_orm(client_config_db).dict()
    mes_analise_str = request.mes_analise.strftime("%Y-%m-%d")

    try:
        caminho_relatorio = orchestrator.executar_fluxo_analise_cliente(
            cliente_config=client_config_dict,
            mes_analise_atual_str=mes_analise_str,
            metricas_selecionadas=request.metricas_selecionadas
        )
        if caminho_relatorio:
            return {"message": "Análise concluída com sucesso!", "report_path": str(caminho_relatorio)}
        else:
            raise HTTPException(status_code=500, detail="Análise concluída, mas o relatório final não foi gerado.")
    except Exception as e:
        # Idealmente, logar o erro aqui
        raise HTTPException(status_code=500, detail=f"Erro durante a execução da análise: {e}")

# --- Bloco de Execução ---
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)