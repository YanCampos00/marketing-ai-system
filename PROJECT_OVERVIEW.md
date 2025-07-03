# Visão Geral do Projeto: Marketing AI System v1

Este documento fornece uma análise detalhada da estrutura, tecnologias e componentes do projeto "Marketing AI System v1". O objetivo é servir como um guia de referência técnica para desenvolvedores.

## 1. Resumo Geral

O **Marketing AI System v1** é uma aplicação web full-stack projetada para automatizar tarefas de marketing digital usando inteligência artificial. O sistema é composto por um backend em Python com FastAPI que serve uma API e um frontend em React (TypeScript) que consome essa API. A principal funcionalidade é permitir que um usuário insira uma tarefa em linguagem natural (ex: "analisar a performance do Google Ads para o cliente X"), que é então interpretada por um agente orquestrador que aciona outros agentes especializados para buscar dados, analisá-los e gerar relatórios.

**Atualizações Recentes:**
- Implementado gerenciamento dinâmico de prompts via banco de dados e interface de usuário.
- Melhorias significativas na UI/UX do frontend, incluindo padronização de botões e correção de visibilidade de texto.
- Aprimoramentos no visualizador de relatórios e na lógica de geração de relatórios consolidados e por plataforma.

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
| | pandas | Manipulação e análise de dados |
| | python-dateutil | Extensões para manipulação de datas |
| | tenacity | Biblioteca para retentativas (retries) |
| | tabulate | Formatação de dados tabulares |
| **Frontend** | React (v19) | Biblioteca para construção da interface de usuário |
| | TypeScript | Superset de JavaScript que adiciona tipagem estática |
| | Vite | Ferramenta de build e servidor de desenvolvimento |
| | Axios | Cliente HTTP para realizar requisições à API do backend |
| | Bootstrap & React-Bootstrap | Framework de CSS para estilização e componentes de UI |
| | React-Toastify | Biblioteca para exibir notificações (toasts) |
| | React Router DOM | Gerenciamento de rotas no frontend |
| | React Select | Componente de seleção customizável |
| **Banco de Dados** | SQLite | Banco de dados relacional (arquivo `clients.db`) |

## 3. Arquitetura do Projeto

O projeto é monorepo com duas pastas principais: `/app` para o backend e `/frontend` para o frontend.

-   **`C:/Users/User/Desktop/GitHub/marketing_ai_system_v1/app/`**: Contém toda a lógica do backend.
    -   **`/agents`**: O cérebro da aplicação. Contém os agentes de IA.
    -   **`/config`**: Arquivos de configuração e credenciais. (Prompts agora no DB)
    -   **`/core`**: Serviços centrais, como a conexão com o LLM e o Google Sheets.
    -   **`/db`**: Configuração do banco de dados, modelos ORM e sessões.
    -   **`/middleware`**: Middlewares para a aplicação FastAPI.
    -   **`/reports`**: Diretório para armazenar relatórios gerados.
    -   **`/utils`**: Funções utilitárias reutilizáveis (ex: formatação de dados, manipulação de arquivos, limpeza de dados, métricas de marketing, salvamento de JSON).
    -   **`main.py`**: O ponto de entrada da aplicação FastAPI, onde a API é definida.
-   **`C:/Users/User/Desktop/GitHub/marketing_ai_system_v1/frontend/`**: Contém toda a lógica do frontend.
    -   **`/src`**: Código-fonte da aplicação React.
    -   **`/pages`**: Componentes que representam páginas inteiras da aplicação (HomePage, HistoryPage, PromptManagementPage).
    -   **`/components`**: Componentes de UI reutilizáveis (incluindo modais para adicionar/editar/deletar clientes, análise e visualização de relatórios).
    -   **`/services`**: Lógica para comunicação com a API do backend.
    -   **`/styles`**: Arquivos de estilo customizados.
    -   **`/types`**: Definições de tipos TypeScript.
    -   **`main.tsx`**: Ponto de entrada da aplicação React.
-   **`C:/Users/User/Desktop/GitHub/marketing_ai_system_v1/`**: Raiz do projeto.
    -   **`requirements.txt`**: Dependências do Python.
    -   **`.env`**: Arquivo para variáveis de ambiente (não versionado).
    -   **`PROJECT_OVERVIEW.md`**: Este arquivo.
    -   **`PROXIMOS_PASSOS.md`**: Documento de acompanhamento de tarefas.
    -   **`scripts/`**: Diretório para scripts utilitários (ex: migração de dados).

## 4. Detalhamento dos Arquivos

### Backend (`/app`)

-   **`main.py`**:
    -   Inicializa o FastAPI e o CORS.
    -   Define endpoints para gerenciamento de clientes (CRUD), análise de mídia, listagem e visualização de relatórios.
    -   **NOVO:** Inclui endpoints CRUD para gerenciamento de prompts (`/prompts`).
    -   No `startup`, pré-carrega o `Orchestrator`.
-   **`agents/orchestrator.py`**:
    -   Classe `Orchestrator` que atua como o agente principal.
    -   Orquestra o fluxo de análise de mídia, acionando o `MediaAgent`.
    -   **ATUALIZADO:** Formata e consolida relatórios de múltiplas plataformas para o prompt `consolidated_report` usando o placeholder `{all_platforms_reports}`.
-   **`agents/media_agent.py`**:
    -   Agente especializado em analisar dados de mídia paga.
    -   Usa o `GoogleSheetConnector` para buscar dados.
    -   **ATUALIZADO:** Utiliza o prompt `media_analysis` de forma dinâmica, passando uma lista de métricas para análise via placeholder `{metrics_to_analyze_list_markdown}`.
-   **`core/llm_service.py`**:
    -   Abstrai a comunicação com o provedor de LLM (Google Gemini).
    -   A função `get_llm_service` atua como uma factory, lendo a configuração do `global_config.json` para inicializar o serviço com a chave de API correta.
-   **`core/gsheet_connector.py`**:
    -   Gerencia a conexão com a API do Google Sheets.
    -   Funções para extrair e limpar dados de planilhas.
-   **`db/database.py`**:
    -   Configura a conexão com o banco de dados SQLite usando SQLAlchemy.
    -   Define os modelos ORM para `ClientDB` e **NOVO:** `PromptDB`.
    -   Fornece a função `get_db` para gerenciamento de sessão.
-   **`utils/prompt_loader.py`**:
    -   **ATUALIZADO:** Função `load_prompt` que agora carrega prompts do banco de dados, em vez de arquivos `.txt`.
-   **`app/middleware.py`**: 
    -   **NOVO:** Contém middlewares para a aplicação FastAPI.
-   **`app/utils/data_cleaners.py`**: 
    -   **NOVO:** Funções para limpeza de dados.
-   **`app/utils/data_formatters.py`**: 
    -   **NOVO:** Funções para formatação de dados.
-   **`app/utils/marketing_metrics.py`**: 
    -   **NOVO:** Funções para cálculo de métricas de marketing.
-   **`app/utils/save_json.py`**: 
    -   **NOVO:** Funções para salvar dados em formato JSON.

### Frontend (`/frontend`)

-   **`package.json`**: 
    -   Define scripts e dependências do projeto.
    -   **ATUALIZADO:** Inclui `react-router-dom` e `react-select`.
-   **`src/main.tsx`**: 
    -   Ponto de entrada da aplicação.
-   **`src/App.tsx`**: 
    -   Componente raiz da aplicação.
    -   **ATUALIZADO:** Configura as rotas usando `react-router-dom`, incluindo `/`, `/history` e **NOVO:** `/prompts`.
    -   Inclui o `ToastContainer`.
-   **`src/pages/HomePage.tsx`**: 
    -   Interface principal para gerenciamento de clientes e início de análises.
    -   **ATUALIZADO:** Botões padronizados e link para `PromptManagementPage`.
-   **`src/pages/HistoryPage.tsx`**: 
    -   **NOVO:** Página para visualizar o histórico de análises, com filtros e visualizador de relatórios.
-   **`src/pages/PromptManagementPage.tsx`**: 
    -   **NOVO:** Página para listar, visualizar e editar prompts armazenados no banco de dados.
-   **`src/components/AnalysisModal.tsx`**: 
    -   **ATUALIZADO:** Tipagem aprimorada para métricas selecionadas.
-   **`src/components/ReportViewerModal.tsx`**: 
    -   **ATUALIZADO:** Modal simplificado para exibir o conteúdo de um relatório.
-   **`src/services/api.ts`**: 
    -   **ATUALIZADO:** URL base da API lida de variável de ambiente.
-   **`src/styles/custom.css`**: 
    -   **ATUALIZADO:** Adicionados estilos de hover para botões.
-   **`src/types/index.ts`**: 
    -   **ATUALIZADO:** Novas interfaces para `Report` e `SelectOption`.

---
*Este documento foi gerado automaticamente e será atualizado para refletir as mudanças no projeto.*