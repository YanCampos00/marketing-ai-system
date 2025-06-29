from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import date, datetime # Importar datetime
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware # Importar CORSMiddleware

from app.agents.orchestrator import executar_fluxo_analise_cliente
from app.db.database import SessionLocal, ClientDB, Base, engine
from app.agents.media_agent import METRICAS_DISPONIVEIS # Importar métricas
from app.agents.orchestrator import PASTA_RELATORIOS_BASE # Importar PASTA_RELATORIOS_BASE

app = FastAPI(title="Marketing AI System API", version="1.0.0")

origins = [
    "http://localhost",
    "http://localhost:5173", # Adicione a URL do seu frontend aqui
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Criar tabelas no banco de dados ao iniciar a aplicação
# Isso garante que a tabela 'clients' exista
Base.metadata.create_all(bind=engine)

# Dependency para obter a sessão do DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Modelos Pydantic para validação de dados da API ---
class ClientBase(BaseModel):
    nome_exibicao: str
    contexto_cliente_prompt: str
    planilha_id_ou_nome: str
    google_sheet_tab_name: Optional[str] = None
    meta_sheet_tab_name: Optional[str] = None

class ClientCreate(ClientBase):
    id: str # ID é necessário na criação

class ClientUpdate(ClientBase):
    # Todos os campos são opcionais para atualização
    nome_exibicao: Optional[str] = None
    contexto_cliente_prompt: Optional[str] = None
    planilha_id_ou_nome: Optional[str] = None

class ClientInDB(ClientBase):
    id: str
    class Config:
        from_attributes = True # CORREÇÃO AQUI: orm_mode foi renomeado para from_attributes

class AnalysisRequest(BaseModel):
    client_id: str
    mes_analise: date  # Usar date para garantir formato AAAA-MM-DD
    metricas_selecionadas: List[str] = [] # Lista de métricas que o usuário quer analisar

# --- Endpoints da API ---

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Marketing AI System v1! Visit /docs for API documentation."}

@app.get("/metrics")
async def get_available_metrics():
    # Retorna as chaves do dicionário METRICAS_DISPONIVEIS
    # Adiciona também as métricas base que não são calculadas, mas são importantes para seleção
    base_metrics = ["Spend", "Revenue", "Sessions", "Conversions", "Clicks", "Impressions"]
    all_metrics = list(METRICAS_DISPONIVEIS.keys()) + base_metrics
    # Remove duplicatas e ordena para melhor apresentação
    return sorted(list(set(all_metrics)))

@app.get("/clients", response_model=Dict[str, ClientInDB])
async def get_clients(db: Session = Depends(get_db)):
    clients_db = db.query(ClientDB).all()
    # Converte a lista de objetos ClientDB para um dicionário com ClientInDB
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
    client_config_db = db.query(ClientDB).filter(ClientDB.id == request.client_id).first()
    if not client_config_db:
        raise HTTPException(status_code=404, detail=f"Cliente com ID '{request.client_id}' não encontrado.")

    # Converte o objeto ClientDB para um dicionário compatível com o orquestrador
    client_config_dict = ClientInDB.from_orm(client_config_db).dict()

    # Converter data para string no formato esperado pelo orquestrador
    mes_analise_str = request.mes_analise.strftime("%Y-%m-%d")

    try:
        caminho_relatorio = executar_fluxo_analise_cliente(
            cliente_config=client_config_dict,
            mes_analise_atual_str=mes_analise_str,
            metricas_selecionadas=request.metricas_selecionadas
        )
        if caminho_relatorio:
            return {"message": "Análise concluída com sucesso!", "client_id": request.client_id, "mes_analise": mes_analise_str, "report_path": str(caminho_relatorio)}
        else:
            raise HTTPException(status_code=500, detail="Análise concluída, mas o relatório final não foi gerado ou encontrado.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro durante a execução da análise: {e}")


import os
from pathlib import Path

@app.get("/reports/{client_id}/{mes_analise}")
async def get_report(client_id: str, mes_analise: str, db: Session = Depends(get_db)):
    # Sanitiza os nomes para uso em caminhos de arquivo
    nome_cliente_seguro = "".join(c if c.isalnum() else "_" for c in client_id)
    mes_analise_seguro = mes_analise.replace("-", "_")

    # Buscar o nome de exibição do cliente no DB para construir o caminho correto
    client_db = db.query(ClientDB).filter(ClientDB.id == client_id).first()
    if not client_db:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")
    
    nome_exibicao_seguro = "".join(c if c.isalnum() else "_" for c in client_db.nome_exibicao)

    # Constrói o caminho completo para o arquivo de relatório
    # Assume que a pasta 'reports' está na raiz do projeto
    pasta_raiz_projeto = Path(__file__).parent.parent # Vai para a pasta 'app', depois para a raiz do projeto
    caminho_pasta_relatorios_cliente = pasta_raiz_projeto / "app" / PASTA_RELATORIOS_BASE / nome_exibicao_seguro / mes_analise_seguro
    nome_arquivo_relatorio_final = f"{nome_exibicao_seguro}_relatorio_consolidado_{mes_analise_seguro}.txt"
    caminho_completo_relatorio_final = caminho_pasta_relatorios_cliente / nome_arquivo_relatorio_final

    if not caminho_completo_relatorio_final.is_file():
        raise HTTPException(status_code=404, detail="Relatório não encontrado.")

    try:
        with open(caminho_completo_relatorio_final, "r", encoding="utf-8") as f:
            content = f.read()
        return {"report_content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao ler o relatório: {e}")


@app.get("/reports/list")
async def list_reports(db: Session = Depends(get_db)):
    reports_data = []
    pasta_raiz_projeto = Path(__file__).parent.parent # Vai para a pasta 'app', depois para a raiz do projeto
    pasta_base_relatorios = pasta_raiz_projeto / "app" / PASTA_RELATORIOS_BASE # Caminho correto para app/reports

    if not pasta_base_relatorios.exists():
        print(f"[DEBUG LIST REPORTS] Pasta base de relatórios não encontrada: {pasta_base_relatorios}")
        return []

    for client_dir in pasta_base_relatorios.iterdir():
        if client_dir.is_dir():
            sanitized_display_name_from_folder = client_dir.name # e.g., "John_John"

            # Encontra o cliente no DB cujo nome de exibição sanitizado corresponde ao nome da pasta
            found_client_db = None
            all_clients = db.query(ClientDB).all()
            for c in all_clients:
                if "".join(char if char.isalnum() else "_" for char in c.nome_exibicao) == sanitized_display_name_from_folder:
                    found_client_db = c
                    break

            if not found_client_db:
                print(f"[DEBUG LIST REPORTS] Cliente não encontrado no DB para pasta: {sanitized_display_name_from_folder}")
                continue

            actual_client_id = found_client_db.id # Este é o ID real do cliente do DB
            nome_exibicao_cliente = found_client_db.nome_exibicao

            for month_dir in client_dir.iterdir():
                if month_dir.is_dir():
                    mes_analise_seguro = month_dir.name
                    # Tenta converter o nome da pasta do mês para o formato AAAA-MM-DD
                    try:
                        mes_analise_formatado = mes_analise_seguro.replace("_", "-")
                        # Validação básica de data
                        datetime.strptime(mes_analise_formatado, "%Y-%m-%d")
                    except ValueError:
                        print(f"[DEBUG LIST REPORTS] Nome de pasta de mês inválido: {mes_analise_seguro}")
                        continue # Ignora pastas de mês com nome inválido

                    # Constrói o nome do arquivo de relatório consolidado
                    # Usa o nome sanitizado da pasta para o nome do arquivo, pois é assim que ele é salvo
                    nome_arquivo_relatorio_final = f"{sanitized_display_name_from_folder}_relatorio_consolidado_{mes_analise_seguro}.txt"
                    caminho_completo_relatorio_final = month_dir / nome_arquivo_relatorio_final

                    print(f"[DEBUG LIST REPORTS] Tentando encontrar arquivo: {caminho_completo_relatorio_final}")
                    if caminho_completo_relatorio_final.is_file():
                        print(f"[DEBUG LIST REPORTS] Arquivo encontrado: {caminho_completo_relatorio_final}")
                        reports_data.append({
                            "client_id": actual_client_id, # Usa o ID real do cliente do DB
                            "client_name": nome_exibicao_cliente,
                            "mes_analise": mes_analise_formatado,
                            "file_name": nome_arquivo_relatorio_final,
                            "file_path": str(caminho_completo_relatorio_final) # Caminho completo para referência
                        })
                    else:
                        print(f"[DEBUG LIST REPORTS] Arquivo NÃO encontrado: {caminho_completo_relatorio_final}")
    # Ordena os relatórios por data decrescente
    reports_data.sort(key=lambda x: datetime.strptime(x["mes_analise"], "%Y-%m-%d"), reverse=True)
    return reports_data
