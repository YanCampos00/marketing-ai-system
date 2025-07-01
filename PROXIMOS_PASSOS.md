# Próximos Passos para o Projeto "Marketing AI System"

Este documento descreve os próximos passos sugeridos para a evolução e aprimoramento do projeto, com base em sua estrutura e funcionalidades atuais.

---

## 1. Refatoração e Melhoria Contínua

-   **Abstração de Fontes de Dados:**
    -   Refatorar o `MediaAgent` para que a lógica de busca de dados seja mais abstrata. Criar "conectores" específicos para cada fonte de dados (um para Google Sheets, outro para uma API direta do Google Ads, etc.), que implementem uma interface comum.
-   **Variáveis de Ambiente:**
    -   Garantir que todas as informações sensíveis e configurações de ambiente (chaves de API, caminhos de arquivos, etc.) sejam carregadas exclusivamente a partir de variáveis de ambiente (`.env`) e não estejam "hardcoded" no código.