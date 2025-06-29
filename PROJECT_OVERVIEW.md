
# Visão Geral do Projeto: Marketing AI System v1

Este documento fornece uma análise detalhada da estrutura, tecnologias e componentes do projeto "Marketing AI System v1". O objetivo é servir como um guia de referência técnica para desenvolvedores.

## 1. Resumo Geral

O **Marketing AI System v1** é uma aplicação web full-stack projetada para automatizar tarefas de marketing digital usando inteligência artificial. O sistema é composto por um backend em Python com FastAPI que serve uma API e um frontend em React (TypeScript) que consome essa API. A principal funcionalidade é permitir que um usuário insira uma tarefa em linguagem natural (ex: "analisar a performance do Google Ads para o cliente X"), que é então interpretada por um agente orquestrador que aciona outros agentes especializados para buscar dados, analisá-los e gerar relatórios.

## 2. Tecnologias Principais

| Camada | Tecnologia/Biblioteca | Propósito |
| :--- | :--- | :--- |
| **Backend** | Python 3.13 | Linguagem principal |
| | FastAPI | Framework web para a criação da API REST |
| | Uvicorn | Servidor ASGI para rodar a aplicação FastAPI |
| | Google Generative AI (Gemini) | Provedor de LLM para as capacidades de IA |
| | GSpread & OAuth2Client | Conexão e autenticação com Google Sheets |
| | SQLAlchemy | ORM para interação com o banco de dados |
| | python-dotenv | Gerenciamento de variáveis de ambiente |
| **Frontend** | React (v19) | Biblioteca para construção da interface de usuário |
| | TypeScript | Superset de JavaScript que adiciona tipagem estática |
| | Vite | Ferramenta de build e servidor de desenvolvimento |
| | Axios | Cliente HTTP para realizar requisições à API do backend |
| | Bootstrap & React-Bootstrap | Framework de CSS para estilização e componentes de UI |
| | React-Toastify | Biblioteca para exibir notificações (toasts) |
| **Banco de Dados** | SQLite | Banco de dados relacional (arquivo `clients.db`) |

## 3. Arquitetura do Projeto

O projeto é monorepo com duas pastas principais: `/app` para o backend e `/frontend` para o frontend.

-   **`C:/Users/User/Desktop/GitHub/marketing_ai_system_v1/app/`**: Contém toda a lógica do backend.
    -   **`/agents`**: O cérebro da aplicação. Contém os agentes de IA.
    -   **`/config`**: Arquivos de configuração, prompts e credenciais.
    -   **`/core`**: Serviços centrais, como a conexão com o LLM e o Google Sheets.
    -   **`/db`**: Configuração do banco de dados, modelos ORM e sessões.
    -   **`/utils`**: Funções utilitárias reutilizáveis (ex: formatação de dados, manipulação de arquivos).
    -   **`main.py`**: O ponto de entrada da aplicação FastAPI, onde a API é definida.
-   **`C:/Users/User/Desktop/GitHub/marketing_ai_system_v1/frontend/`**: Contém toda a lógica do frontend.
    -   **`/src`**: Código-fonte da aplicação React.
    -   **`/pages`**: Componentes que representam páginas inteiras da aplicação.
    -   **`/components`**: Componentes de UI reutilizáveis.
    -   **`/services`**: Lógica para comunicação com a API do backend.
    -   **`main.tsx`**: Ponto de entrada da aplicação React.
-   **`C:/Users/User/Desktop/GitHub/marketing_ai_system_v1/`**: Raiz do projeto.
    -   **`requirements.txt`**: Dependências do Python.
    -   **`.env`**: Arquivo para variáveis de ambiente (não versionado).
    -   **`PROJECT_OVERVIEW.md`**: Este arquivo.

## 4. Detalhamento dos Arquivos

### Backend (`/app`)

-   **`main.py`**:
    -   Inicializa o FastAPI e o CORS.
    -   Monta o diretório `static` e `templates`.
    -   Define o endpoint principal `/` (que serve o `index.html`) e o endpoint `/execute_task` (POST).
    -   No `startup`, pré-carrega o `Orchestrator` para evitar recarregar o modelo de IA a cada requisição.
-   **`agents/orchestrator.py`**:
    -   Classe `Orchestrator` que atua como o agente principal.
    -   Recebe a tarefa do usuário e usa o LLM para determinar a "intenção" e extrair entidades (como nome do cliente e fonte de dados) através do prompt `intent_recognition`.
    -   Com base na intenção, delega a tarefa para um agente especializado (atualmente, o `MediaAgent`).
-   **`agents/media_agent.py`**:
    -   Agente especializado em analisar dados de mídia paga.
    -   Usa o `GoogleSheetConnector` para buscar dados de uma planilha nomeada no formato `{client_name}_{data_source}`.
    -   Usa o prompt `media_analysis` para enviar os dados ao LLM e gerar um relatório.
-   **`core/llm_service.py`**:
    -   Abstrai a comunicação com o provedor de LLM (Google Gemini).
    -   A função `get_llm_service` atua como uma factory, lendo a configuração do `global_config.json` para inicializar o serviço com a chave de API correta.
-   **`core/gsheet_connector.py`**:
    -   Gerencia a conexão com a API do Google Sheets usando credenciais de conta de serviço.
    -   O método `get_data_from_sheet` busca todos os valores de uma aba específica.
-   **`db/database.py`**:
    -   Configura a conexão com o banco de dados SQLite usando SQLAlchemy.
    -   Fornece a função `get_db` para ser usada como uma dependência do FastAPI, gerenciando o ciclo de vida da sessão do banco de dados.
-   **`utils/prompt_loader.py`**:
    -   Função `load_prompt` que carrega dinamicamente arquivos `.txt` da pasta `app/config/prompts/`. Essencial para manter os prompts separados da lógica de código.

### Frontend (`/frontend`)

-   **`package.json`**:
    -   Define os scripts (`dev`, `build`, `lint`) e as dependências do projeto.
    -   Dependências notáveis: `axios`, `react`, `react-bootstrap`, `typescript`.
-   **`vite.config.ts`**:
    -   Configuração padrão do Vite para um projeto React.
-   **`src/main.tsx`**:
    -   Ponto de entrada da aplicação. Renderiza o componente `App` no elemento `#root` do `index.html`.
    -   Importa os estilos globais do Bootstrap e um arquivo de CSS customizado.
-   **`src/App.tsx`**:
    -   Componente raiz da aplicação.
    -   Renderiza a `HomePage`.
    -   Inclui o `ToastContainer` para exibir notificações em toda a aplicação.
-   **`src/pages/HomePage.tsx` (Assumido, baseado no `App.tsx`)**:
    -   Provavelmente contém a interface principal onde o usuário digita a tarefa e vê o resultado.
    -   Deve conter um campo de texto/área de texto e um botão para submeter a tarefa.
    -   Deve usar `axios` para chamar o endpoint `/execute_task` do backend.
    -   Deve gerenciar o estado de carregamento (loading) e exibir os resultados ou erros retornados pela API.

---
*Este documento foi gerado automaticamente e será atualizado para refletir as mudanças no projeto.*
