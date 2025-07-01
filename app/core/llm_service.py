import google.generativeai as genai
import os
from app.config.config_loader import load_config

class LLMService:
    """
    Serviço para interagir com o modelo de linguagem (LLM).
    Atualmente, suporta o Google Generative AI (Gemini).
    """
    def __init__(self, provider: str, api_key: str):
        self.provider = provider
        self.api_key = api_key
        if self.provider == 'google':
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
        else:
            raise ValueError(f"Provedor LLM '{self.provider}' não suportado.")

    def generate_text(self, prompt: str, max_retries=3):
        """
        Gera texto usando o LLM a partir de um prompt.

        Args:
            prompt (str): O prompt para enviar ao modelo.
            max_retries (int): Número máximo de tentativas em caso de falha.

        Returns:
            str: O texto gerado pelo modelo.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Erro ao gerar texto com o LLM: {e}")
            # Implementar lógica de retentativa se necessário
            return "Ocorreu um erro ao gerar a resposta."

def get_llm_service():
    """
    Função factory para criar uma instância do LLMService
    com base na configuração global.
    """
    config = load_config('app/config/global_config.json')
    provider = config.get('llm_provider', 'google')
    api_key_env = config.get('google_api_key_env')
    
    api_key = os.getenv(api_key_env)
    if not api_key:
        raise ValueError(f"A variável de ambiente '{api_key_env}' não está definida.")
        
    return LLMService(provider=provider, api_key=api_key)