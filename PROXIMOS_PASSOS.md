# Próximos Passos e Melhorias Sugeridas

Este documento delineia as próximas tarefas e melhorias planejadas para o projeto, com base em uma análise crítica do código-fonte. As tarefas estão organizadas por prioridade e área.

--- 

## 1. Concluído Recentemente

-   [x] **Refatoração do `MediaAgent`**: A lógica foi dividida em métodos privados menores e mais coesos (`_fetch_and_clean_data`, `_calculate_metrics`, etc.), melhorando a legibilidade e a manutenibilidade.
-   [x] **Validação de Dados na API**: Foram implementados validadores Pydantic (`@field_validator`) nos modelos de entrada para garantir a integridade dos dados.
-   [x] **Centralização de Configurações**: As variáveis de ambiente e configurações são agora gerenciadas pela classe `Settings` em `app/config/settings.py` usando `pydantic-settings`.
-   [x] **Endpoint de Métricas Dinâmico**: O endpoint `GET /metrics` agora busca a lista de métricas diretamente do `MediaAgent`, tornando-a dinâmica.
-   [x] **Centralização de Caminhos de Relatórios**: A função `get_report_path` em `app/utils/file_utils.py` agora centraliza a lógica de nomenclatura e criação de caminhos de relatórios.
-   [x] **Gerenciamento de Estado Global no Frontend**: Foram implementados `ClientContext` e `PromptContext` para gerenciar o estado global e evitar chamadas de API repetitivas.
-   [x] **Tratamento de Erros Centralizado no Frontend**: Interceptadores do Axios foram configurados em `src/services/api.ts` para padronizar o tratamento de erros.
-   [x] **Refatoração de Estilos CSS**: Estilos inline foram movidos para arquivos `.css` e padronizados com classes. A lista de clientes na `HomePage` foi refatorada para usar um componente `client-card` totalmente customizado, resolvendo problemas de alinhamento e altura inconsistente.

--- 

## 2. Próximas Tarefas (Prioridade)

-   [ ] **(Backend) Implementar Testes Automatizados com `pytest`**:
    -   **Tarefa:** Criar testes de unidade para as funções em `app/utils/`. Focar em `data_cleaners`, `data_formatters` e `marketing_metrics`.
    -   **Tarefa:** Criar testes de integração para os endpoints da API usando o `TestClient` do FastAPI. Cobrir os fluxos de CRUD de clientes e o endpoint de análise.

-   [ ] **(Frontend) Implementar Testes com `Vitest` e `React Testing Library`**:
    -   **Tarefa:** Criar testes de unidade para componentes de UI puros (ex: botões, modais).
    -   **Tarefa:** Criar testes de interação para os principais fluxos do usuário, como adicionar um cliente, iniciar uma análise e visualizar um relatório.

-   [ ] **(Backend) Implementar Tarefas em Background para Análises**:
    -   **Tarefa:** Refatorar o endpoint `/analyze` para usar `BackgroundTasks` do FastAPI. A API deve retornar uma resposta imediata (ex: `202 Accepted`), e a análise deve rodar em segundo plano. Isso evita timeouts no cliente para análises longas.
    -   **Melhoria Futura:** Considerar uma solução mais robusta como Celery se as tarefas se tornarem muito complexas ou demoradas.

--- 

## 3. Melhorias Futuras (Menor Prioridade)

-   [ ] **Implementar Containerização com Docker**:
    -   **Tarefa:** Criar um `Dockerfile` para o backend e um para o frontend.
    -   **Tarefa:** Criar um arquivo `docker-compose.yml` para orquestrar a execução de ambos os serviços, simplificando a configuração do ambiente de desenvolvimento e preparando para o deploy.

-   [ ] **Configurar Pipeline de CI/CD com GitHub Actions**:
    -   **Tarefa:** Criar um workflow que, a cada push para a branch principal, execute automaticamente:
        1.  Instalação de dependências (Python e Node.js).
        2.  Execução de linters (`ruff` e `eslint`).
        3.  Execução de todos os testes automatizados (backend e frontend).

-   [ ] **(Frontend) Adicionar Paginação ou Scroll Infinito**:
    -   **Tarefa:** Na `HistoryPage`, implementar paginação ou scroll infinito para a lista de relatórios, melhorando a performance caso a lista se torne muito grande.
