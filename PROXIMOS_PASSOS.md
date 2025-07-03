# Próximos Passos e Melhorias Sugeridas

Este documento delineia as próximas tarefas e melhorias planejadas para o projeto, com base em uma análise crítica do código-fonte. As tarefas estão organizadas por área para facilitar o desenvolvimento.

---

## 1. Backend (Python / FastAPI)

-   [x] **Refatorar `MediaAgent.run`**:
    -   **Tarefa:** Quebrar a função `run` em `app/agents/media_agent.py` em métodos privados menores e mais focados para melhorar a legibilidade e a testabilidade.

-   [x] **Implementar Validação de Dados com Pydantic**:
    -   **Tarefa:** Adicionar validadores (`@field_validator`) aos modelos Pydantic em `app/main.py` para garantir a integridade dos dados na entrada da API (ex: validar o formato do ID do cliente).

-   [x] **Centralizar Configurações com `pydantic-settings`**:
    -   **Tarefa:** Criar uma classe de configuração centralizada para carregar e validar todas as variáveis de ambiente (`DATABASE_URL`, `GOOGLE_API_KEY`, etc.) em um único lugar, garantindo que a aplicação não inicie se uma variável crítica estiver faltando.

-   [x] **Tornar o Endpoint de Métricas Dinâmico**:
    -   **Tarefa:** Modificar o endpoint `GET /metrics` em `app/main.py` para que ele consuma dinamicamente a lista de métricas disponíveis a partir do `MediaAgent`, em vez de usar uma lista estática.

-   [x] **Centralizar Lógica de Caminhos de Relatórios**:
    -   **Tarefa:** Criar uma função utilitária em `app/utils/file_utils.py` (ex: `get_report_path(client_name, analysis_date)`) para centralizar a lógica de nomenclatura e criação de caminhos para os arquivos de relatório.

-   [ ] **Implementar Tarefas em Background para Análises**:
    -   **Tarefa (Futura):** Refatorar o endpoint `/analyze` para usar `BackgroundTasks` do FastAPI (ou uma solução mais robusta como Celery) para executar a análise. A API deve retornar imediatamente um `task_id`, e o frontend deve consultar o status da tarefa.

---

## 2. Frontend (React / TypeScript)

-   [x] **Implementar Gerenciamento de Estado Global**:
    -   **Tarefa:** Utilizar o **React Context** para gerenciar o estado global de clientes e prompts.
    -   **Ações:** Criar um `ClientProvider` e um `PromptProvider` que buscarão os dados uma vez e os fornecerão para todos os componentes filhos, evitando chamadas repetidas à API.

-   [x] **Centralizar Tratamento de Erros da API**:
    -   **Tarefa:** Usar **interceptadores do Axios** em `src/services/api.ts` para criar um manipulador de erros de resposta global. Isso irá padronizar o feedback de erro (ex: toasts) e remover a lógica repetida de `catch` dos componentes.

-   [x] **Refatorar Estilos CSS**:
    -   **Tarefa:** Mover todos os estilos inline (`style={{...}}`) para o arquivo `src/styles/custom.css` e usar nomes de classe.
    -   **Exemplo:** Criar classes como `.btn-cta`, `.btn-edit`, `.btn-delete` para padronizar a aparência dos botões.

---

## 3. Melhorias de Arquitetura e Boas Práticas

-   [ ] **(Prioridade Alta) Implementar Estrutura de Testes Automatizados**:
    -   **Tarefa (Backend):** Configurar `pytest`. Criar testes de unidade para as funções em `app/utils/` e para a lógica dos agentes. Criar testes de integração para os endpoints da API usando o `TestClient` do FastAPI.
    -   **Tarefa (Frontend):** Configurar `Vitest` e `React Testing Library`. Criar testes de unidade para componentes de UI e testes de interação para os principais fluxos do usuário (ex: adicionar um cliente, iniciar uma análise).

-   [ ] **(Futuro) Implementar Containerização com Docker**:
    -   **Tarefa:** Criar um `Dockerfile` para o serviço de backend (`app`).
    -   **Tarefa:** Criar um `Dockerfile` para o serviço de frontend (`frontend`).
    -   **Tarefa:** Criar um arquivo `docker-compose.yml` para orquestrar a execução de ambos os contêineres, simplificando a configuração do ambiente de desenvolvimento e o deploy.

-   [ ] **(Futuro) Configurar Pipeline de CI/CD**:
    -   **Tarefa:** Criar um workflow do GitHub Actions que seja acionado a cada push ou pull request.
    -   **Passos do Workflow:**
        1.  Instalar dependências (Python e Node.js).
        2.  Executar linters (`ruff` e `eslint`).
        3.  Executar todos os testes automatizados (backend e frontend).
        4.  (Opcional) Construir a aplicação para produção (`npm run build`).
