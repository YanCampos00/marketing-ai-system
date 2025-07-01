import os
import json

def save_to_file(filepath, content):
    """
    Salva o conteúdo em um arquivo de texto.
    Se o conteúdo for um dicionário ou lista, tenta salvar como JSON formatado.
    Caso contrário, salva como texto simples.
    """
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            if isinstance(content, dict):
                json.dump(content, f, indent=2, ensure_ascii=False)
                print(f"Conteúdo JSON salvo em: {filepath}")
            elif isinstance(content, list):
                json.dump(content, f, indent=2, ensure_ascii=False)
                print(f"Conteúdo JSON salvo em: {filepath}")
            else:
                f.write(str(content))
                print(f"Conteúdo de texto salvo em: {filepath}")
    except Exception as e:
        print(f"Erro ao salvar arquivo {filepath}: {e}")

def read_from_json(file_path: str) -> dict:
    """
    Lê dados de um arquivo JSON.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_directory_if_not_exists(path: str):
    """
    Cria um diretório se ele não existir.
    """
    if not os.path.exists(path):
        os.makedirs(path)

def get_report_path(client_name: str, mes_analise: str, file_type: str = "consolidated") -> str:
    """
    Gera o caminho completo para um arquivo de relatório.

    Args:
        client_name (str): O nome do cliente.
        mes_analise (str): O mês da análise no formato 'AAAA-MM-DD'.
        file_type (str): O tipo de arquivo (ex: 'consolidated', 'google_ads_kpis', 'meta_ads_kpis').

    Returns:
        str: O caminho absoluto para o arquivo de relatório.
    """
    safe_client_name = "".join(c if c.isalnum() else "_" for c in client_name)
    safe_mes_analise = mes_analise.replace("-", "_")
    
    reports_base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'reports')
    client_report_dir = os.path.join(reports_base_dir, safe_client_name, safe_mes_analise)
    
    create_directory_if_not_exists(client_report_dir)

    if file_type == "consolidated":
        file_name = f"{safe_client_name}_relatorio_consolidado_{safe_mes_analise}.txt"
    elif file_type == "google_ads_kpis":
        file_name = f"google_ads_kpis_output_{safe_mes_analise}.json"
    elif file_type == "meta_ads_kpis":
        file_name = f"meta_ads_kpis_output_{safe_mes_analise}.json"
    else:
        raise ValueError(f"Tipo de arquivo de relatório desconhecido: {file_type}")

    return os.path.join(client_report_dir, file_name)