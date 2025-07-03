class PromptTemplateError(Exception):
    """Exceção para erros relacionados a templates de prompt."""
    pass

class LLMConnectionError(Exception):
    """Exceção para erros de conexão com o serviço de LLM."""
    pass

class DataSourceError(Exception):
    """Exceção para erros relacionados a fontes de dados (ex: planilhas)."""
    pass

class ErroProcessamentoDadosAgente(Exception):
    """Classe base para erros específicos do processamento de dados dos agentes."""
    pass

class PlanilhaNaoEncontradaError(ErroProcessamentoDadosAgente):
    """Erro lançado quando a planilha Google Sheets não é encontrada."""
    pass

class AbaNaoEncontradaError(ErroProcessamentoDadosAgente):
    """Erro lançado quando uma aba específica não é encontrada na planilha."""
    pass

class ColunaNaoEncontradaError(ErroProcessamentoDadosAgente):
    """Erro lançado quando uma coluna essencial não é encontrada nos dados da planilha."""
    pass

class ErroLeituraDadosError(ErroProcessamentoDadosAgente):
    """Erro genérico lançado durante a leitura ou processamento inicial dos dados da planilha."""
    pass

class FormatoDataInvalidoError(ErroProcessamentoDadosAgente):
    """Erro lançado quando o formato da data no str_mes_analise_atual é inválido."""
    pass