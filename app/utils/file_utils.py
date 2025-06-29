import os
import json
from app.utils.save_json import salvar_json_kpis # Importação corrigida

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
                # Previne salvar dicionários gigantes com markdown
                if "markdown" in content and "caminho_json" in content:
                    print(f"[AVISO] Tentativa de salvar dicionário de retorno do agente inteiro! Salve apenas o JSON de KPIs.")
                    f.write(str(content))  # Ou apenas salve o markdown, se quiser
                else:
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

def carregar_kpis_json(caminho_arquivo_json):
    """
    Lê e retorna o dicionário de um arquivo JSON salvo com KPIs.
    Retorna None se o arquivo não existir ou houver erro de leitura.
    """
    if not os.path.exists(caminho_arquivo_json):
        print(f"[file_utils] Arquivo JSON não encontrado: {caminho_arquivo_json}")
        return None
    try:
        with open(caminho_arquivo_json, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[file_utils] Erro ao carregar JSON: {e}")
        return None
    

def gerar_caminho_kpis_json(plataforma, mes_analise, cliente_nome=None):
    """
    Gera o caminho do arquivo JSON de KPIs para o cliente/plataforma/mês.
    Exemplo de saída: app/reports/cliente_seguro/mes_seguro/plataforma_segura_mes_seguro.json
    """
    # Caminho para o diretório do arquivo atual (file_utils.py)
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    # Caminho para o diretório 'app'
    app_dir = os.path.dirname(current_file_dir)
    # Caminho para a raiz do projeto (marketing_ai_system_v1)
    project_root_dir = os.path.dirname(app_dir)

    # Agora, construa o caminho para 'app/reports' a partir da raiz do projeto
    pasta_base_relatorios = os.path.join(project_root_dir, "app", "reports")

    plataforma_folder = plataforma.lower().replace(" ", "_")
    mes_analise_file = mes_analise.replace(" ", "_")

    if cliente_nome:
        cliente_folder = cliente_nome.lower().replace(" ", "_")
        pasta_destino = os.path.join(pasta_base_relatorios, cliente_folder, mes_analise_file)
        nome_arquivo = f"{plataforma_folder}_kpis_output_{mes_analise_file}.json"
    else:
        # Fallback, embora cliente_nome deva ser sempre fornecido
        pasta_destino = os.path.join(pasta_base_relatorios, plataforma_folder, mes_analise_file)
        nome_arquivo = f"{plataforma_folder}_kpis_output_{mes_analise_file}.json"

    os.makedirs(pasta_destino, exist_ok=True)
    return os.path.join(pasta_destino, nome_arquivo)
