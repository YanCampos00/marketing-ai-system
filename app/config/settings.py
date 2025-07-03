from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Carrega e valida as variáveis de ambiente da aplicação.
    """
    # Carrega as variáveis do arquivo .env
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra='ignore')

    # Configurações do Banco de Dados
    DATABASE_URL: str = "sqlite:///./app/db/clients.db"

    # Configurações do LLM
    LLM_PROVIDER: str = "google"
    GOOGLE_API_KEY: str

    # Configurações do Google Sheets
    GOOGLE_CREDS_PATH: str

    # Configurações do Servidor
    PORT: int = 8000

# Cria uma instância única das configurações para ser importada em outros módulos
settings = Settings()
