# Próximos Passos para o Projeto "Marketing AI System"

Este documento descreve os próximos passos sugeridos para a evolução e aprimoramento do projeto, com base em sua estrutura e funcionalidades atuais.

## Prioridades Críticas (Análise de Código)

Estas são as tarefas mais urgentes identificadas na análise de código. Devem ser resolvidas antes de novas funcionalidades.

1.  **Corrigir Inconsistência Funcional entre Frontend e Backend:**
    -   **Status:** `CONCLUÍDO`. Os problemas de visibilidade de texto e exibição do relatório foram resolvidos.

2.  **Corrigir Risco de Segurança (Credenciais Expostas):**
    -   **Status:** `CONCLUÍDO`. O arquivo `app/config/credenciais.json` foi adicionado ao `.gitignore`.

3.  **Externalizar Configurações "Hardcoded":**
    -   **Status:** `CONCLUÍDO`. As configurações de `DATABASE_URL`, `GOOGLE_CREDS_PATH` e `VITE_API_BASE_URL` foram movidas para variáveis de ambiente.

4.  **Melhorar a Tipagem no Frontend:**
    -   **Status:** `CONCLUÍDO`.
    -   **Problema:** Uso do tipo `any[]` para o estado `metricasSelecionadas` no componente `AnalysisModal.tsx`.
    -   **Ação:** Definir uma interface `SelectOption { value: string; label: string; }` e utilizar `SelectOption[]` para garantir a segurança de tipo.

---

## 1. Melhorar o Tratamento de Erros e Feedback ao Usuário
-   **Status:** `CONCLUÍDO`.
-   **Backend:**
    -   Implementar exceções customizadas mais granulares para diferenciar erros (ex: `ClienteNaoEncontradoError`, `FonteDeDadosError`, `LLMError`).
    -   Criar um *middleware* no FastAPI para capturar todas as exceções não tratadas e retornar respostas de erro padronizadas em JSON.
-   **Frontend:**
    -   Utilizar as respostas de erro padronizadas do backend para exibir mensagens claras e úteis ao usuário usando `react-toastify`. Por exemplo: "Erro: A planilha para o cliente 'XPTO' não foi encontrada. Verifique o nome e tente novamente."
    -   Adicionar estados visuais mais claros para carregamento, sucesso e erro nos componentes.


## 2. Interface de Usuário (UI) Mais Rica e Interativa
-   **Status:** `CONCLUÍDO`.
-   **Visualização de Dados:**
    -   Substituir a exibição de relatórios em texto puro por componentes de UI mais ricos.
    -   Integrar uma biblioteca de gráficos (como `Chart.js` ou `Recharts`) para exibir os KPIs (Custo, ROI, CTR, etc.) em gráficos de linha, barra ou pizza.
    -   Apresentar os dados tabulares em tabelas interativas com ordenação e filtros.
-   **Histórico de Tarefas:**
    -   Implementar uma funcionalidade para que o usuário possa ver um histórico das últimas tarefas executadas e seus respectivos resultados.

## 3. Autenticação e Autorização de Usuários

-   **Backend:**
    -   Implementar um sistema de autenticação baseado em tokens (ex: JWT) com endpoints para login (`/token`) e registro de usuários.
    -   Proteger os endpoints da API para que apenas usuários autenticados possam executar tarefas.
-   **Frontend:**
    -   Criar uma página de login.
    -   Gerenciar o estado de autenticação do usuário (armazenar o token de forma segura).
    -   Implementar rotas protegidas que só são acessíveis após o login.

## 4. Melhorar a Gestão de Configuração

-   **Prompts Dinâmicos:**
    -   Em vez de carregar prompts de arquivos de texto, armazená-los no banco de dados. Isso permitiria que os prompts fossem editados através de uma interface de administrador sem a necessidade de fazer deploy de uma nova versão do código.
-   **Configurações de Clientes:**
    -   Expandir o modelo de `Client` no banco de dados para incluir configurações específicas, como o ID da planilha do Google Sheets, chaves de API para outras plataformas, etc. O `MediaAgent` passaria a buscar essa informação do banco em vez de inferir pelo nome.

## 5. Refatoração e Melhoria Contínua

-   **Abstração de Fontes de Dados:**
    -   Refatorar o `MediaAgent` para que a lógica de busca de dados seja mais abstrata. Criar "conectores" específicos para cada fonte de dados (um para Google Sheets, outro para uma API direta do Google Ads, etc.), que implementem uma interface comum.
-   **Variáveis de Ambiente:**
    -   Garantir que todas as informaç��es sensíveis e configurações de ambiente (chaves de API, caminhos de arquivos, etc.) sejam carregadas exclusivamente a partir de variáveis de ambiente (`.env`) e não estejam "hardcoded" no código.
