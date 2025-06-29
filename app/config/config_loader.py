import json
import os

RAIZ_DO_PROJETO_CONFIG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CAMINHO_CLIENTS_CONFIG = os.path.join(RAIZ_DO_PROJETO_CONFIG, 'config', 'clients_config.json')
CAMINHO_GLOBAL_CONFIG = os.path.join(RAIZ_DO_PROJETO_CONFIG, 'config', 'global_config.json')


def carregar_config_clientes(caminho_arquivo=CAMINHO_CLIENTS_CONFIG):
    """
    Carrega as configurações dos clientes do arquivo JSON.
    Retorna um dicionário com as configurações ou um dicionário vazio se o arquivo não existir.
    Retorna None em caso de erro crítico de leitura ou JSON inválido.
    """
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            configs = json.load(f)
        return configs
    except FileNotFoundError:
        print(f"AVISO: Arquivo de configuração de clientes '{caminho_arquivo}' não encontrado. Será criado um novo ao salvar.")
        return {}
    except json.JSONDecodeError:
        print(f"Erro Crítico: Arquivo de configuração de clientes '{caminho_arquivo}' não é um JSON válido. Verifique o arquivo.")
        return None
    except Exception as e:
        print(f"Erro inesperado ao carregar '{caminho_arquivo}': {e}")
        return None


def salvar_config_clientes(configs, caminho_arquivo=CAMINHO_CLIENTS_CONFIG):
    """
    Salva as configurações dos clientes no arquivo JSON.
    Retorna True se bem-sucedido, False caso contrário.
    """
    try:
        os.makedirs(os.path.dirname(caminho_arquivo), exist_ok=True)
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            json.dump(configs, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Erro ao salvar configurações de clientes em '{caminho_arquivo}': {e}")
        return False


def carregar_config_global(caminho_arquivo=CAMINHO_GLOBAL_CONFIG):
    """Carrega as configurações globais da aplicação."""
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("Configurações globais carregadas com sucesso.")
        return config
    except FileNotFoundError:
        print(f"AVISO: Arquivo de configuração global '{caminho_arquivo}' não encontrado. Usando padrões se disponíveis.")
        return {}
    except json.JSONDecodeError:
        print(f"Erro Crítico: Arquivo de configuração global '{caminho_arquivo}' não é um JSON válido.")
        return None
    except Exception as e:
        print(f"Erro inesperado ao carregar config global de '{caminho_arquivo}': {e}")
        return None
