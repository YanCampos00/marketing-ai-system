import json
import os
import google.generativeai as genai
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
from datetime import datetime

from app.agents.base_agent import Agent
from app.agents.media_agent import get_media_data_tool, media_instructions_template
from app.utils.file_utils import save_to_file, carregar_kpis_json
from app.utils.custom_exceptions import (
    PlanilhaNaoEncontradaError, AbaNaoEncontradaError, ColunaNaoEncontradaError,
    ErroLeituraDadosError, FormatoDataInvalidoError, ErroProcessamentoDadosAgente
)
from app.config.config_loader import carregar_config_global 

# Carrega configurações globais no nível do módulo
_global_config_loaded = carregar_config_global()
if _global_config_loaded is None:
    print("Falha crítica ao carregar configurações globais. Usando configurações padrão vazias.")
    global_config = {}
else:
    global_config = _global_config_loaded

print(f"[ORCHESTRATOR - MÓDULO] global_config carregado: {global_config}")

PASTA_RELATORIOS_BASE = "reports"

def _inicializar_servicos_apis():
    # Acessa a variável global_config diretamente do módulo
    llm_model_name = global_config.get("llm_model_name", "models/gemini-2.5-flash-preview-04-17-thinking")
    load_dotenv()
    api_key_gemini = os.getenv("GEMINI_API_KEY")
    if not api_key_gemini:
        print("\nErro Crítico: Chave da API do Gemini (GEMINI_API_KEY) não encontrada no arquivo .env.\n")
        return None, None

    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    credenciais_path = os.path.join(script_dir, "config", "credenciais.json")

    llm_model = None
    gspread_client = None

    try:
        genai.configure(api_key=api_key_gemini)
        llm_model = genai.GenerativeModel(model_name=llm_model_name)
        print(f"Modelo Gemini '{llm_model_name}' inicializado com sucesso.")
    except Exception as e:
        print(f"\nErro Crítico ao configurar o modelo Gemini: {e}")
        return None, None

    if not os.path.exists(credenciais_path):
        print(f"\nErro Crítico: Arquivo de credenciais '{credenciais_path}' NÃO FOI ENCONTRADO.\n")
        return llm_model, None

    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(credenciais_path, scope)
        gspread_client = gspread.authorize(creds)
        print("Cliente Google Sheets inicializado com sucesso.")
        return llm_model, gspread_client
    except Exception as e:
        print(f"\nErro Crítico ao conectar com Google Sheets ou ler credenciais: {e}\n")
        return llm_model, None

def _orchestrator_data_processor(data_inputs):
    """
    Processa os dados de entrada para o Agente Orquestrador.
    Neste caso, os dados já vêm pré-formatados, então apenas os retorna.
    """
    return data_inputs

def _executar_agente_midia(
    agente_obj: Agent, 
    gspread_client,
    plataforma_nome,
    nome_planilha,
    nome_aba,
    colunas_extras,
    metricas_selecionadas,
    contexto_cliente,
    mes_analise_str,
    nome_cliente_id,
    caminho_pasta_relatorios_cliente,
    cliente_nome_para_kpis # Novo parâmetro
    ):
    print(f"\n--- {agente_obj.name} ({plataforma_nome}): Preparando dados --- ")
    kpis_json = None
    caminho_json = None

    tool_input_params = {
        "plataforma": plataforma_nome,
        "nome_planilha": nome_planilha,
        "nome_aba": nome_aba,
        "colunas_extras": colunas_extras,
        "metricas_selecionadas": metricas_selecionadas # Passa as métricas selecionadas
    }

    try:
        resultado_agente = agente_obj.run(
            gspread_client=gspread_client, 
            tool_input_params=tool_input_params,
            cliente_contexto=contexto_cliente, 
            mes_analise_atual_param=mes_analise_str,
            extra_tool_params=None, 
            kpis_json=None,  # Será carregado abaixo
            caminho_json=None
        )
        if not isinstance(resultado_agente, dict):
            print(f"Retorno do agente não é um dict! Retorno: {resultado_agente}")
            return {"kpis_json_data": None, "analise_textual_data": "Erro: retorno inesperado do agente."}

        # Pegue o caminho do JSON salvo pelo agente
        caminho_json = resultado_agente.get("caminho_json")
        kpis_json = carregar_kpis_json(caminho_json) if caminho_json else None

        analise_textual_str = resultado_agente.get("analise_textual")
        raw_llm_response = resultado_agente.get("raw_llm_response", "")
        markdown_input_data = resultado_agente.get("data_markdown")

        # Salva o markdown de entrada para log/debug
        if markdown_input_data and not (isinstance(markdown_input_data, str) and "Erro:" in markdown_input_data):
            nome_arquivo_markdown = f"{nome_cliente_id}_{plataforma_nome.lower().replace(' ', '_')}_input_markdown_{mes_analise_str}.txt"
            caminho_completo_markdown = os.path.join(caminho_pasta_relatorios_cliente, nome_arquivo_markdown)
            save_to_file(caminho_completo_markdown, markdown_input_data)

        # Salva o output JSON dos KPIs do agente de plataforma
        if kpis_json:
            print(f"[DEBUG ORCHESTRATOR] KPIs JSON para {plataforma_nome}: {json.dumps(kpis_json, indent=2)}")
            nome_arquivo_kpi_json = f"{nome_cliente_id}_{plataforma_nome.lower().replace(' ', '_')}_kpis_output_{mes_analise_str}.json"
            caminho_completo_kpi_json = os.path.join(caminho_pasta_relatorios_cliente, nome_arquivo_kpi_json)
            save_to_file(caminho_completo_kpi_json, kpis_json)

        # Salva a análise textual
        if analise_textual_str:
            nome_arquivo_analise_txt = f"{nome_cliente_id}_{plataforma_nome.lower().replace(' ', '_')}_analise_textual_output_{mes_analise_str}.txt"
            caminho_completo_analise_txt = os.path.join(caminho_pasta_relatorios_cliente, nome_arquivo_analise_txt)
            save_to_file(caminho_completo_analise_txt, analise_textual_str)

        return {
            "kpis_json_data": kpis_json, 
            "analise_textual_data": analise_textual_str,
            "raw_llm_response_data": raw_llm_response
        }
    
    except (PlanilhaNaoEncontradaError, AbaNaoEncontradaError, ColunaNaoEncontradaError, 
            ErroLeituraDadosError, FormatoDataInvalidoError, ErroProcessamentoDadosAgente) as e_agente:
        print(f"Erro de dados ao processar para {agente_obj.name} ({plataforma_nome}): {e_agente}")
        error_output = f"ErroDados_{plataforma_nome.replace(' ', '')}: {e_agente}"
        nome_arquivo_erro = f"{nome_cliente_id}_{plataforma_nome.lower().replace(' ', '_')}_ERROR_{mes_analise_str}.txt"
        caminho_completo_erro = os.path.join(caminho_pasta_relatorios_cliente, nome_arquivo_erro)
        save_to_file(caminho_completo_erro, error_output)
        return {"kpis_json_data": None, "analise_textual_data": error_output}

    except Exception as e_inesperado:
        print(f"Erro inesperado durante a execução do {agente_obj.name} ({plataforma_nome}): {e_inesperado}")
        error_output = f"ErroInesperado_{plataforma_nome.replace(' ', '')}: {e_inesperado}"
        nome_arquivo_erro = f"{nome_cliente_id}_{plataforma_nome.lower().replace(' ', '_')}_ERROR_{mes_analise_str}.txt"
        caminho_completo_erro = os.path.join(caminho_pasta_relatorios_cliente, nome_arquivo_erro)
        save_to_file(caminho_completo_erro, error_output)
        return {"kpis_json_data": None, "analise_textual_data": error_output}

def _preparar_input_para_orchestrator(resultado_agente_plataforma, nome_plataforma_para_erro):
    kpis_obj = resultado_agente_plataforma.get("kpis_json_data")
    analise_str = resultado_agente_plataforma.get("analise_textual_data")

    if isinstance(analise_str, str) and \
       ("ErroDados_" in analise_str or "ErroInesperado_" in analise_str or "Erro:" in analise_str):
        kpis_json_formatado = json.dumps({"ERRO": f"Dados de {nome_plataforma_para_erro} indisponíveis ou com erro: {analise_str}"}, indent=2, ensure_ascii=False)
        analise_textual_formatada = analise_str
        return kpis_json_formatado, analise_textual_formatada

    if kpis_obj is None or not isinstance(kpis_obj, dict):
        kpis_json_formatado = json.dumps({"ERRO": f"KPIs JSON de {nome_plataforma_para_erro} não puderam ser processados ou estão ausentes."}, indent=2, ensure_ascii=False)
    else:
        kpis_json_formatado = json.dumps(kpis_obj, indent=2, ensure_ascii=False)
    
    analise_textual_formatada = analise_str if analise_str else f"Análise textual de {nome_plataforma_para_erro} não disponível."
    return kpis_json_formatado, analise_textual_formatada

def executar_fluxo_analise_cliente(cliente_config, mes_analise_atual_str, metricas_selecionadas):
    print(f"[ORCHESTRATOR - FUNÇÃO] global_config no início da função: {global_config}")

    nome_cliente_exibicao = cliente_config.get('nome_exibicao', 'ClienteDesconhecido')
    nome_cliente_seguro = "".join(c if c.isalnum() else "_" for c in nome_cliente_exibicao) # Sanitização consistente
    mes_analise_seguro = mes_analise_atual_str.replace("-", "_")

    llm_model = None # Inicializa llm_model antes do try
    gspread_client = None

    try:
        llm_model, gspread_client = _inicializar_servicos_apis()
    except Exception as e:
        print(f"[ERROR] Erro inesperado ao inicializar serviços de API: {e}")
        return None # Retorna None se houver erro na inicialização

    if not llm_model:
        print("Falha crítica ao inicializar o modelo LLM. Análise abortada.")
        return None
    
    # Ajuste do caminho da pasta de relatórios para a nova estrutura
    # Caminho para o diretório do arquivo atual (orchestrator.py)
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    # Caminho para o diretório 'app'
    app_dir = os.path.dirname(current_file_dir)
    # Caminho para a raiz do projeto (marketing_ai_system_v1)
    project_root_dir = os.path.dirname(app_dir)

    # Agora, construa o caminho para 'app/reports' a partir da raiz do projeto
    caminho_pasta_relatorios_cliente = os.path.join(project_root_dir, "app", PASTA_RELATORIOS_BASE, nome_cliente_seguro, mes_analise_seguro)
    os.makedirs(caminho_pasta_relatorios_cliente, exist_ok=True)

    nome_planilha_consolidada = cliente_config["planilha_id_ou_nome"]
    contexto_cliente_prompt = cliente_config["contexto_cliente_prompt"]

    nome_aba_google = cliente_config.get("google_sheet_tab_name", 
                                               global_config.get("default_google_ads_tab_name", "Dados Google Ads"))
    nome_aba_meta = cliente_config.get("meta_sheet_tab_name", 
                                             global_config.get("default_meta_ads_tab_name", "Dados Meta Ads"))

    try:
        data_analise_dt_obj = datetime.strptime(mes_analise_atual_str, "%Y-%m-%d")
        nome_mes_analise_formatado = data_analise_dt_obj.strftime("%B de %Y")
    except ValueError:
        print(f"Erro: Formato de data inválido para o mês de análise '{mes_analise_atual_str}'. Use AAAA-MM-DD.")
        return

    agente_midia = Agent(
        name="Agente de Mídia",
        instructions_template=media_instructions_template.replace("{dados_markdown_summary_month_name}", nome_mes_analise_formatado),
        data_tool_function=get_media_data_tool, 
        llm_model=llm_model
    )

    # Executar Agente de Mídia para Google Ads
    resultado_google = _executar_agente_midia(
        agente_midia, gspread_client, "Google Ads", nome_planilha_consolidada, nome_aba_google,
        [], metricas_selecionadas, contexto_cliente_prompt, mes_analise_atual_str,
        nome_cliente_seguro, caminho_pasta_relatorios_cliente,
        cliente_nome_para_kpis=nome_cliente_seguro # Passa o nome do cliente para o agente de mídia
    )

    # Executar Agente de Mídia para Meta Ads
    resultado_meta = _executar_agente_midia(
        agente_midia, gspread_client, "Meta Ads", nome_planilha_consolidada, nome_aba_meta,
        [], metricas_selecionadas, contexto_cliente_prompt, mes_analise_atual_str,
        nome_cliente_seguro, caminho_pasta_relatorios_cliente,
        cliente_nome_para_kpis=nome_cliente_seguro # Passa o nome do cliente para o agente de mídia
    )

    google_kpis_json_str, google_analise_textual_str = _preparar_input_para_orchestrator(resultado_google, "Google Ads")
    meta_kpis_json_str, meta_analise_textual_str = _preparar_input_para_orchestrator(resultado_meta, "Meta Ads")

    erro_nos_inputs_orchestrator = "indisponíveis ou com erro" in google_analise_textual_str or \
                              "indisponíveis ou com erro" in meta_analise_textual_str or \
                              "não puderam ser processados" in google_kpis_json_str or \
                              "não puderam ser processados" in meta_kpis_json_str
    
    if erro_nos_inputs_orchestrator:
        print("\nAgente Orquestrador não executado devido a erros nos dados dos agentes de mídia.")
        if "ERRO" in google_kpis_json_str or "indisponíveis" in google_analise_textual_str :
             print(f"Detalhe Google: KPIs JSON: {google_kpis_json_str}, Análise: {google_analise_textual_str}")
        if "ERRO" in meta_kpis_json_str or "indisponíveis" in meta_analise_textual_str:
             print(f"Detalhe Meta: KPIs JSON: {meta_kpis_json_str}, Análise: {meta_analise_textual_str}")
        print("Análise interrompida.")
        return

    orchestrator_tool_inputs = {
        "google_kpis_json": google_kpis_json_str,
        "google_analise_textual": google_analise_textual_str,
        "meta_kpis_json": meta_kpis_json_str,
        "meta_analise_textual": meta_analise_textual_str,
        "mes_analise_formatado": nome_mes_analise_formatado,
        "cliente_contexto": contexto_cliente_prompt
    }
    
    # Importar o prompt do orquestrador aqui para evitar circular dependency
    from app.utils.prompt_loader import carregar_prompt_de_arquivo
    PROMPT_FILE_PATH_ORCHESTRATOR = "app/config/prompts/orchestrator_prompt.txt"
    orchestrator_instructions_template = carregar_prompt_de_arquivo(PROMPT_FILE_PATH_ORCHESTRATOR)

    if orchestrator_instructions_template is None:
        print("ERRO CRÍTICO: Template de instruções do Agente Orquestrador não pôde ser carregado. A aplicação pode não funcionar corretamente.")
        orchestrator_instructions_template = "ERRO DE CARREGAMENTO DE PROMPT - ORCHESTRATOR"

    agente_orchestrator = Agent(
        name="Agente Orquestrador",
        instructions_template=orchestrator_instructions_template,
        data_tool_function=_orchestrator_data_processor, # Adiciona a função de processamento de dados
        llm_model=llm_model
    )

    print(f"\n--- {agente_orchestrator.name}: Preparando relatório consolidado --- ")
    try:
        resultado_orchestrator = agente_orchestrator.run(
            gspread_client=None, 
            tool_input_params=None,
            cliente_contexto=contexto_cliente_prompt, 
            extra_tool_params=orchestrator_tool_inputs
        )
        relatorio_final_orchestrator = resultado_orchestrator["llm_response_manager"] 
        
        print(f"\n📄 RELATÓRIO FINAL CONSOLIDADO PARA {nome_cliente_exibicao} ({nome_mes_analise_formatado}):\n")
        print(relatorio_final_orchestrator)
        
        if not (isinstance(relatorio_final_orchestrator, str) and "Erro:" in relatorio_final_orchestrator):
            nome_arquivo_relatorio_final = f"{nome_cliente_seguro}_relatorio_consolidado_{mes_analise_seguro}.txt"
            caminho_completo_relatorio_final = os.path.join(caminho_pasta_relatorios_cliente, nome_arquivo_relatorio_final)
            save_to_file(caminho_completo_relatorio_final, relatorio_final_orchestrator)
            return caminho_completo_relatorio_final # Retorna o caminho do relatório
        return None # Retorna None se houver erro ou não for salvo
            
    except Exception as e_orchestrator:
        print(f"Erro ao executar o {agente_orchestrator.name}: {e_orchestrator}")
        return None # Retorna None em caso de exceção
            
    print("Execução do fluxo de análise concluída.")