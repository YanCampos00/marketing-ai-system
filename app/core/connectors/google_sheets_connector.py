import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import pandas as pd
import traceback
import logging

from app.config.settings import settings # Importar settings
from app.utils.custom_exceptions import (
    PlanilhaNaoEncontradaError,
    AbaNaoEncontradaError,
    ColunaNaoEncontradaError,
    ErroLeituraDadosError
)
from app.utils.data_cleaners import limpar_numero
from app.core.connectors.base_connector import BaseConnector

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class GoogleSheetsConnector(BaseConnector):
    """
    Conector para extrair dados do Google Sheets.
    Implementa a interface BaseConnector.
    """
    def __init__(self):
        self.creds_path = settings.GOOGLE_CREDS_PATH
        
        if not os.path.exists(self.creds_path):
            raise FileNotFoundError(f"Arquivo de credenciais não encontrado: {self.creds_path}")
        
        # O escopo padrão para a API do Google Sheets v4
        self.scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(self.creds_path, self.scope)
        self.client = gspread.authorize(self.creds)

    def get_data(self, data_source: str, client_config: dict, mes_analise: str) -> pd.DataFrame:
        """
        Busca e limpa dados de uma aba específica do Google Sheets.
        """
        spreadsheet_name = client_config.get("planilha_id_ou_nome")
        
        if data_source == 'google_ads':
            sheet_tab_name = client_config.get('google_sheet_tab_name')
        elif data_source == 'meta_ads':
            sheet_tab_name = client_config.get('meta_sheet_tab_name')
        else:
            raise ValueError(f"Fonte de dados desconhecida para o GoogleSheetsConnector: {data_source}")

        if not spreadsheet_name or not sheet_tab_name:
            raise ErroLeituraDadosError(f"Configuração da planilha (nome ou aba) incompleta para '{data_source}' do cliente '{client_config.get('nome_exibicao')}'.")

        try:
            worksheet = self.client.open(spreadsheet_name).worksheet(sheet_tab_name)
            all_data = worksheet.get_all_records()
            
            if not all_data:
                return pd.DataFrame() # Retorna DataFrame vazio se não houver dados

            df = pd.DataFrame(all_data)
            
            # A lógica de limpeza e transformação que estava no MediaAgent pode ser movida para cá
            # ou permanecer no agente, dependendo do nível de abstração desejado.
            # Por enquanto, vamos manter a limpeza no agente para ele ter controle sobre o formato.
            
            return df

        except gspread.exceptions.SpreadsheetNotFound as e:
            raise PlanilhaNaoEncontradaError(f"Planilha '{spreadsheet_name}' não encontrada.")
        except gspread.exceptions.WorksheetNotFound as e:
            raise AbaNaoEncontradaError(f"Aba '{sheet_tab_name}' não encontrada na planilha '{spreadsheet_name}'.")
        except Exception as e:
            logger.error(f"Erro inesperado ao extrair dados do Google Sheets: {e}")
            traceback.print_exc()
            raise ErroLeituraDadosError(f"Erro inesperado ao ler dados da planilha: {e}")
