import os
import sys
from sqlalchemy.orm import Session

# Adiciona o diretório raiz do projeto ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.database import SessionLocal, PromptDB, Base, engine

# Garante que as tabelas sejam criadas, incluindo a nova tabela de prompts
Base.metadata.create_all(bind=engine)

PROMPT_FILES_DIR = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), 'app', 'config', 'prompts')

def migrate_prompts():
    db: Session = SessionLocal()
    try:
        for filename in os.listdir(PROMPT_FILES_DIR):
            if filename.endswith('.txt'):
                prompt_name = os.path.splitext(filename)[0]
                file_path = os.path.join(PROMPT_FILES_DIR, filename)
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Verifica se o prompt já existe
                existing_prompt = db.query(PromptDB).filter(PromptDB.nome == prompt_name).first()
                
                if existing_prompt:
                    print(f"Prompt '{prompt_name}' já existe. Atualizando conteúdo.")
                    existing_prompt.conteudo = content
                    existing_prompt.descricao = f"Migrado de {filename}" # Atualiza descrição se necessário
                else:
                    print(f"Adicionando prompt '{prompt_name}'.")
                    new_prompt = PromptDB(id=prompt_name, nome=prompt_name, conteudo=content, descricao=f"Migrado de {filename}")
                    db.add(new_prompt)
        
        db.commit()
        print("Migração de prompts concluída com sucesso!")
    except Exception as e:
        db.rollback()
        print(f"Erro durante a migração de prompts: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate_prompts()
