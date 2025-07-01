import json
import os

def load_config(file_path: str):
    """
    Carrega um arquivo de configuração JSON.

    Args:
        file_path (str): O caminho para o arquivo JSON.

    Returns:
        dict: O conteúdo do arquivo JSON como um dicionário.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_credentials():
    """
    Carrega as credenciais do Google a partir do arquivo especificado
    na variável de ambiente GOOGLE_APPLICATION_CREDENTIALS.
    """
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path:
        raise ValueError("Variável de ambiente GOOGLE_APPLICATION_CREDENTIALS não definida.")
    
    return load_config(creds_path)