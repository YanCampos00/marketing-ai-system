import os
from app.utils.custom_exceptions import PromptTemplateError
from app.db.database import SessionLocal, PromptDB

def load_prompt(prompt_name: str) -> str:
    """
    Carrega um template de prompt do banco de dados.

    Args:
        prompt_name (str): O nome do prompt a ser carregado.

    Returns:
        str: O conteúdo do template do prompt.
    """
    db = SessionLocal()
    try:
        prompt_db = db.query(PromptDB).filter(PromptDB.nome == prompt_name).first()
        if not prompt_db:
            raise PromptTemplateError(f"O template de prompt '{prompt_name}' não foi encontrado no banco de dados.")
        return prompt_db.conteudo
    except PromptTemplateError:
        raise # Re-raise a exceção customizada
    except Exception as e:
        raise PromptTemplateError(f"Erro ao carregar o prompt '{prompt_name}' do banco de dados: {e}")
    finally:
        db.close()