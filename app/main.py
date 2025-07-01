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
from app.db.database import get_db, engine, Base, ClientDB, PromptDB
from app.middleware import add_exception_handlers
# from app.agents.media_agent import METRICAS_DISPONIVEIS # Removido

# Cria as tabelas no banco de dados (se não existirem)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Marketing AI System API", version="1.1.0")

# Adiciona os manipuladores de exceção customizados
add_exception_handlers(app)

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

# --- New Pydantic Models for Reports ---
class ReportSummary(BaseModel):
    client_id: str
    client_name: str
    mes_analise: str
    file_name: str
    file_path: str

class ReportContent(BaseModel):
    report_content: str

class PromptBase(BaseModel):
    nome: str
    conteudo: str
    descricao: Optional[str] = None

class PromptCreate(PromptBase):
    pass

class PromptInDB(PromptBase):
    id: str
    class Config:
        from_attributes = True

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
    # Lista estática de métricas. Idealmente, isso viria do MediaAgent de forma dinâmica.
    return sorted([
        "Spend", "Revenue", "Sessions", "Conversions", "Clicks", "Impressions",
        "ROI", "CPS", "TKM", "Conversion_Rate", "CPC", "CPM"
    ])

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

@app.post("/prompts", response_model=PromptInDB)
async def create_prompt(prompt: PromptCreate, db: Session = Depends(get_db)):
    db_prompt = db.query(PromptDB).filter(PromptDB.nome == prompt.nome).first()
    if db_prompt:
        raise HTTPException(status_code=400, detail=f"Prompt com nome '{prompt.nome}' já existe.")
    db_prompt = PromptDB(**prompt.dict())
    db.add(db_prompt)
    db.commit()
    db.refresh(db_prompt)
    return db_prompt

@app.get("/prompts", response_model=List[PromptInDB])
async def get_all_prompts(db: Session = Depends(get_db)):
    prompts = db.query(PromptDB).all()
    return prompts

@app.get("/prompts/{prompt_name}", response_model=PromptInDB)
async def get_prompt_by_name(prompt_name: str, db: Session = Depends(get_db)):
    db_prompt = db.query(PromptDB).filter(PromptDB.nome == prompt_name).first()
    if not db_prompt:
        raise HTTPException(status_code=404, detail=f"Prompt com nome '{prompt_name}' não encontrado.")
    return db_prompt

@app.put("/prompts/{prompt_name}", response_model=PromptInDB)
async def update_prompt(prompt_name: str, prompt_data: PromptCreate, db: Session = Depends(get_db)):
    db_prompt = db.query(PromptDB).filter(PromptDB.nome == prompt_name).first()
    if not db_prompt:
        raise HTTPException(status_code=404, detail=f"Prompt com nome '{prompt_name}' não encontrado.")
    for key, value in prompt_data.dict(exclude_unset=True).items():
        setattr(db_prompt, key, value)
    db.commit()
    db.refresh(db_prompt)
    return db_prompt

@app.delete("/prompts/{prompt_name}")
async def delete_prompt(prompt_name: str, db: Session = Depends(get_db)):
    db_prompt = db.query(PromptDB).filter(PromptDB.nome == prompt_name).first()
    if not db_prompt:
        raise HTTPException(status_code=404, detail=f"Prompt com nome '{prompt_name}' não encontrado.")
    db.delete(db_prompt)
    db.commit()
    return {"message": f"Prompt '{prompt_name}' removido com sucesso."}

@app.post("/analyze")
async def run_analysis(request: AnalysisRequest, db: Session = Depends(get_db)):
    orchestrator: Orchestrator = app.state.orchestrator
    client_config_db = db.query(ClientDB).filter(ClientDB.id == request.client_id).first()
    if not client_config_db:
        raise HTTPException(status_code=404, detail=f"Cliente com ID '{request.client_id}' não encontrado.")

    client_config_dict = ClientInDB.from_orm(client_config_db).dict()
    mes_analise_str = request.mes_analise.strftime("%Y-%m-%d")

    # O bloco try/except foi removido daqui. As exceções agora serão capturadas pelo middleware.
    caminho_relatorio = orchestrator.executar_fluxo_analise_cliente(
        cliente_config=client_config_dict,
        mes_analise_atual_str=mes_analise_str,
        metricas_selecionadas=request.metricas_selecionadas
    )
    if caminho_relatorio:
        return {"message": "Análise concluída com sucesso!", "report_path": str(caminho_relatorio)}
    else:
        # Se o fluxo terminar sem erro mas não retornar um caminho, algo está errado.
        raise HTTPException(status_code=500, detail="Análise concluída, mas o relatório final não foi gerado.")

@app.get("/reports/list", response_model=List[ReportSummary])
async def list_reports(db: Session = Depends(get_db)):
    reports_list = []
    reports_base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports')

    clients_db = db.query(ClientDB).all()
    client_map = {client.id: client.nome_exibicao for client in clients_db}
    
    if not os.path.exists(reports_base_dir):
        return []

    for client_dir_name in os.listdir(reports_base_dir):
        client_dir_path = os.path.join(reports_base_dir, client_dir_name)
        if os.path.isdir(client_dir_path):
            # Tenta encontrar o client_id correspondente ao safe_client_name
            found_client_id = None
            original_client_name = None
            for client_db_entry in clients_db:
                generated_safe_name = "".join(c if c.isalnum() else "_" for c in client_db_entry.nome_exibicao)
                if generated_safe_name == client_dir_name:
                    found_client_id = client_db_entry.id
                    original_client_name = client_db_entry.nome_exibicao
                    break
            
            if not found_client_id:
                continue # Pula diretórios que não correspondem a um cliente conhecido

            for month_dir_name in os.listdir(client_dir_path):
                month_dir_path = os.path.join(client_dir_path, month_dir_name)
                if os.path.isdir(month_dir_path):
                    mes_analise_formatted = month_dir_name.replace("_", "-") # Converte para YYYY-MM-DD

                    report_file_pattern = f"{client_dir_name}_relatorio_consolidado_{month_dir_name}.txt"
                    
                    for file_name in os.listdir(month_dir_path):
                        if file_name == report_file_pattern:
                            reports_list.append(ReportSummary(
                                client_id=found_client_id,
                                client_name=original_client_name,
                                mes_analise=mes_analise_formatted,
                                file_name=file_name,
                                file_path=os.path.join(client_dir_name, month_dir_name, file_name) # Caminho relativo
                            ))
    return reports_list

@app.get("/reports/view/{file_name}", response_model=ReportContent)
async def get_report_content_by_filename(file_name: str):
    reports_base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports')
    
    # O file_name pode conter o caminho relativo, então precisamos encontrá-lo
    # Esta é uma busca simples, pode ser otimizada se necessário
    for root, dirs, files in os.walk(reports_base_dir):
        if file_name in files:
            report_file_path = os.path.join(root, file_name)
            try:
                with open(report_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return ReportContent(report_content=content)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Erro ao ler o relatório: {e}")
    
    raise HTTPException(status_code=404, detail="Relatório não encontrado.")


@app.get("/reports/{client_id}/{mes_analise}", response_model=ReportContent)
async def get_report_content(client_id: str, mes_analise: str, db: Session = Depends(get_db)):
    client_db_entry = db.query(ClientDB).filter(ClientDB.id == client_id).first()
    if not client_db_entry:
        raise HTTPException(status_code=404, detail=f"Cliente com ID '{client_id}' não encontrado.")
    
    original_client_name = client_db_entry.nome_exibicao
    safe_client_name = "".join(c if c.isalnum() else "_" for c in original_client_name)
    
    safe_mes_analise = mes_analise.replace("-", "_") # Converte para YYYY_MM_DD para o caminho do arquivo

    reports_base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports')
    report_file_path = os.path.join(
        reports_base_dir,
        safe_client_name,
        safe_mes_analise,
        f"{safe_client_name}_relatorio_consolidado_{safe_mes_analise}.txt"
    )

    if not os.path.exists(report_file_path):
        raise HTTPException(status_code=404, detail="Relatório não encontrado.")

    try:
        with open(report_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return ReportContent(report_content=content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao ler o relatório: {e}")

# --- Bloco de Execução ---
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False) # 'reload=True' pode causar problemas no Windows