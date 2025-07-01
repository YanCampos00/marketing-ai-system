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