# Visão Geral do Projeto: Marketing AI System v1

Este documento fornece uma análise detalhada da estrutura, tecnologias e componentes do projeto "Marketing AI System v1". O objetivo é servir como um guia de referência técnica para desenvolvedores.

## 1. Resumo Geral

O **Marketing AI System v1** é uma aplicação web full-stack projetada para automatizar a análise de performance de marketing digital. O sistema combina um backend em Python (FastAPI) e um frontend em React (TypeScript). A funcionalidade central permite que os usuários selecionem um cliente e um período para análise. O sistema então busca dados de plataformas como Google Ads e Meta Ads, realiza cálculos de KPI, compara períodos e utiliza um Large Language Model (LLM) para gerar relatórios textuais detalhados e consolidados.

**Funcionalidades Principais:**
- **Backend API**: Gerenciamento de Clientes e Prompts (CRUD), orquestração de análise, listagem e visualização de relatórios.
- **Frontend UI**: Interface para interagir com a API, permitindo gerenciar clientes, iniciar análises, visualizar histórico de relatórios e gerenciar prompts.
- **Orquestração de IA**: Um agente orquestrador gerencia o fluxo de trabalho, delegando a coleta e análise de dados a agentes especializados.
- **Geração de Relatórios**: O sistema gera relatórios individuais por plataforma (Google, Meta) e um relatório consolidado que resume a performance geral.

## 2. Tecnologias Principais

| Camada | Tecnologia/Biblioteca | Propósito |
| :--- | :--- | :--- |
| **Backend** | Python 3.13 | Linguagem principal |
| | FastAPI | Framework web para a criação da API REST |
| | Uvicorn | Servidor ASGI para rodar a aplicação FastAPI |
| | SQLAlchemy | ORM para interação com o banco de dados |
| | Pydantic | Validação de dados e configurações (`pydantic-settings`) |
| | Google Generative AI | Provedor de LLM (Gemini) para as capacidades de IA |
| | GSpread & OAuth2Client | Conexão e autenticação com Google Sheets |
| | pandas | Manipulação e análise de dados |
| | pytest | Framework para testes automatizados |
| **Frontend** | React (v19) | Biblioteca para construção da interface de usuário |
| | TypeScript | Superset de JavaScript que adiciona tipagem estática |
| | Vite | Ferramenta de build e servidor de desenvolvimento |
| | Axios | Cliente HTTP para requisições à API (com interceptadores) |
| | React Router DOM | Gerenciamento de rotas no frontend |
| | React Context | Gerenciamento de estado global (Clientes, Prompts) |
| | Bootstrap & React-Bootstrap | Framework de CSS e componentes de UI |
| | React-Toastify | Exibição de notificações (toasts) |
| **Banco de Dados** | SQLite | Banco de dados relacional (arquivo `clients.db`) |

## 3. Arquitetura do Projeto

O projeto segue uma estrutura de monorepo com duas pastas principais: `/app` (backend) e `/frontend`.

-   **`/app`**: Contém a lógica do backend em Python.
    -   **`/agents`**: O cérebro da aplicação.
        -   `orchestrator.py`: Agente principal que coordena o fluxo de análise.
        -   `media_agent.py`: Agente especializado que busca, limpa, calcula e analisa dados de plataformas de mídia.
    -   **`/core`**: Serviços centrais.
        -   `llm_service.py`: Abstrai a comunicação com o LLM.
        -   `/connectors`: Conectores para fontes de dados externas (ex: `google_sheets_connector.py`).
    -   **`/db`**: Configuração do banco de dados (`database.py`) com modelos SQLAlchemy (`ClientDB`, `PromptDB`).
    -   **`/config`**: Configurações da aplicação, incluindo `settings.py` que usa `pydantic-settings` para carregar variáveis de ambiente.
    -   **`/utils`**: Funções utilitárias para manipulação de arquivos, formatação de dados, etc.
    -   **`/middleware.py`**: Middlewares customizados, como o de tratamento de exceções.
    -   **`/reports`**: Diretório onde os relatórios gerados são armazenados.
    -   **`main.py`**: Ponto de entrada da API FastAPI, onde todos os endpoints são definidos.

-   **`/frontend`**: Contém a aplicação frontend em React.
    -   **`/src/pages`**: Componentes que representam as páginas da aplicação (`HomePage`, `HistoryPage`, `PromptManagementPage`).
    -   **`/src/components`**: Componentes de UI reutilizáveis (Modais, Botões, etc.).
    -   **`/src/context`**: Provedores de Contexto (`ClientContext`, `PromptContext`) para gerenciamento de estado global.
    -   **`/src/services`**: Lógica de comunicação com a API, incluindo a instância do Axios e interceptadores de erro.
    -   **`/src/styles`**: Arquivos de estilo customizados (`custom.css`) que definem a aparência geral e estilizam componentes específicos, como os cards de cliente na HomePage.
    -   **`/src/types`**: Definições de tipos TypeScript.
    -   **`App.tsx`**: Componente raiz que configura o roteamento da aplicação.

---
*Este documento foi gerado com base na análise do código-fonte e será atualizado para refletir as mudanças no projeto.*