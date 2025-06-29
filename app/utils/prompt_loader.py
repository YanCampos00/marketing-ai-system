import os

RAIZ_DO_PROJETO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def carregar_prompt_de_arquivo(caminho_relativo_ao_projeto):
    """
    Lê e retorna o conteúdo de um arquivo de prompt.
    O caminho_relativo_ao_projeto deve ser o caminho a partir da raiz do projeto.
    Ex: "prompts/google_agent_prompt.txt"
    """
    caminho_absoluto = os.path.join(RAIZ_DO_PROJETO, caminho_relativo_ao_projeto)
    
    try:
        with open(caminho_absoluto, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Erro Crítico: Arquivo de prompt não encontrado em '{caminho_absoluto}'. Verifique o caminho e o nome do arquivo.")
        return None 
    except Exception as e:
        print(f"Erro Crítico ao carregar prompt de '{caminho_absoluto}': {e}")
        return None
