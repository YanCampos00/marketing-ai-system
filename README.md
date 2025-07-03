# Marketing AI System v1

**Marketing AI System v1** é uma aplicação web full-stack que automatiza a análise de performance de campanhas de marketing digital. Utilizando um backend em Python/FastAPI e um frontend em React/TypeScript, o sistema se conecta a fontes de dados (como Google Sheets), processa métricas, e usa um LLM (Google Gemini) para gerar relatórios analíticos detalhados.

## Funcionalidades Principais

-   **API RESTful (FastAPI)**: Endpoints para gerenciar clientes, prompts, e orquestrar análises complexas.
-   **Interface Reativa (React)**: UI para gerenciamento de entidades, início de análises, e visualização de histórico de relatórios.
-   **Análise com IA**: Agentes inteligentes que coletam, processam e interpretam dados de marketing, culminando em relatórios textuais gerados por IA.
-   **Banco de Dados**: Persistência de dados de clientes e prompts via SQLAlchemy com SQLite.
-   **Gerenciamento de Configuração**: Carregamento seguro de configurações e segredos usando `pydantic-settings`.

## Como Executar o Projeto

### Pré-requisitos

-   Python 3.11+
-   Node.js 18+
-   Git

### 1. Configuração do Backend

```bash
# 1. Clone o repositório
git clone <URL_DO_REPOSITORIO>
cd marketing_ai_system_v1

# 2. Crie e ative um ambiente virtual
python -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate

# 3. Instale as dependências do Python
pip install -r requirements.txt

# 4. Configure as variáveis de ambiente
# Crie um arquivo .env na raiz do projeto e adicione as chaves necessárias
# (veja o arquivo .env.example ou app/config/settings.py para referência)
# Exemplo de .env:
# GEMINI_API_KEY="sua_chave_api"
# GOOGLE_APPLICATION_CREDENTIALS="caminho/para/suas/credenciais.json"

# 5. Inicie o servidor do backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Configuração do Frontend

```bash
# 1. Navegue até o diretório do frontend (em um novo terminal)
cd frontend

# 2. Instale as dependências do Node.js
npm install

# 3. Configure a variável de ambiente para a API
# Crie um arquivo .env.local em /frontend e adicione a URL da API
# Exemplo de .env.local:
# VITE_API_BASE_URL="http://localhost:8000"

# 4. Inicie o servidor de desenvolvimento do frontend
npm run dev
```

Após seguir esses passos, a aplicação estará acessível em `http://localhost:5173`.