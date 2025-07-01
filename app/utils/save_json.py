import json
import os
from datetime import datetime

def save_json(data, client_name, data_source):
    """
    Salva os dados em um arquivo JSON estruturado por pastas.

    Args:
        data (dict): Os dados a serem salvos.
        client_name (str): Nome do cliente para criar a pasta.
        data_source (str): Fonte dos dados (ex: 'google_ads') para subpasta.
    """
    # Define o caminho base para os relatórios
    base_path = os.path.join('app', 'reports')
    
    # Cria o caminho completo do diretório
    client_path = os.path.join(base_path, client_name)
    source_path = os.path.join(client_path, data_source)
    
    # Cria os diretórios se não existirem
    os.makedirs(source_path, exist_ok=True)
    
    # Gera um nome de arquivo com timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"{timestamp}_report.json"
    file_path = os.path.join(source_path, file_name)
    
    # Salva o arquivo JSON
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    print(f"Relatório salvo com sucesso em: {file_path}")
    return file_path

def salvar_json_kpis(
    plataforma: str,
    mes_analise: str,
    resumo_periodos: dict,
    comparativos: dict,
    pasta_saida: str,
    sufixo_nome: str = "",
    metricas_selecionadas: list = []
):
    """
    Salva os KPIs processados e filtrados em um arquivo JSON.
    Apenas as métricas selecionadas pelo usuário são salvas.
    """
    # Filtra o resumo do período atual
    kpis_atuais_filtrados = {k: round(v, 2) if isinstance(v, (int, float)) else v for k, v in resumo_periodos.get('atual', {}).items() if k in metricas_selecionadas}

    # Filtra os comparativos (MoM e YoY)
    comparativos_filtrados = {}
    for metrica in metricas_selecionadas:
        mom_key = f"{metrica}_MoM"
        yoy_key = f"{metrica}_YoY"
        if mom_key in comparativos:
            comparativos_filtrados[mom_key] = round(comparativos[mom_key], 2) if isinstance(comparativos[mom_key], (int, float)) else comparativos[mom_key]
        if yoy_key in comparativos:
            comparativos_filtrados[yoy_key] = round(comparativos[yoy_key], 2) if isinstance(comparativos[yoy_key], (int, float)) else comparativos[yoy_key]

    data_to_save = {
        "plataforma": plataforma,
        "mes_analise": mes_analise,
        "kpis_selecionados": kpis_atuais_filtrados,
        "comparativos_selecionados": comparativos_filtrados,
        "metricas_selecionadas": metricas_selecionadas
    }

    os.makedirs(pasta_saida, exist_ok=True)
    # Usar um nome de arquivo consistente baseado no mês de análise, não no timestamp da execução
    safe_sufixo = sufixo_nome.lower().replace(' ', '_')
    safe_mes = mes_analise.replace('-', '_')
    file_name = f"{safe_sufixo}_kpis_output_{safe_mes}.json"

    file_path = os.path.join(pasta_saida, file_name)

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=4)
    print(f"KPIs salvos em: {file_path}")
    return file_path

def carregar_kpis_json(file_path: str):
    """
    Carrega um arquivo JSON de KPIs.
    """
    if not os.path.exists(file_path):
        return None
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)
