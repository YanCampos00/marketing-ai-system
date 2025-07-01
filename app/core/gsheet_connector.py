import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import pandas as pd
import traceback
import logging

from app.config.config_loader import load_config
from app.utils.custom_exceptions import (
    PlanilhaNaoEncontradaError,
    AbaNaoEncontradaError,
    ColunaNaoEncontradaError,
    ErroLeituraDadosError
)
from app.utils.data_cleaners import limpar_numero # Importar a função de limpeza de número

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def extrair_dados_base(
    gspread_client,
    nome_planilha,
    nome_aba,
    colunas_necessarias=None,
    formato_data='%d/%m/%Y'
):
    """
    Extrai e limpa dados do Google Sheets para qualquer plataforma.
    - gspread_client: cliente autenticado do gspread.
    - nome_planilha: nome da planilha no Google Sheets.
    - nome_aba: nome da aba dentro da planilha.
    - colunas_necessarias: lista de colunas obrigatórias (ex: ['Data', 'Investimento', ...])
    - formato_data: formato esperado da coluna 'Data'.
    Retorna: DataFrame filtrado e limpo.
    """
    try:
        worksheet = gspread_client.open(nome_planilha).worksheet(nome_aba)
        all_data = worksheet.get_all_records()
        logger.info(f"[DEBUG GSHEET] Dados brutos de '{nome_planilha}' - '{nome_aba}': {all_data[:2]}") # Primeiras 2 linhas

        if not all_data:
            raise ErroLeituraDadosError(
                f"Nenhum dado encontrado na planilha '{nome_planilha}', aba '{nome_aba}'."
            )
        df = pd.DataFrame(all_data)
        logger.info(f"[DEBUG GSHEET] DataFrame inicial após pd.DataFrame ({nome_planilha} - {nome_aba}):\n{df.head()}\n{df.dtypes}")

        # Verificação das colunas obrigatórias
        if colunas_necessarias is not None:
            for col in colunas_necessarias:
                if col not in df.columns:
                    raise ColunaNaoEncontradaError(
                        f"Coluna obrigatória '{col}' não encontrada na planilha '{nome_planilha}', aba '{nome_aba}'."
                    )

        # Limpeza da coluna Data
        if 'Data' in df.columns:
            df['Data'] = pd.to_datetime(df['Data'], format=formato_data, errors='coerce')
            df = df.dropna(subset=['Data'])

        # Limpeza de números (exceto 'Data')
        # Aplica limpar_numero apenas para colunas que estão no DataFrame e não são a coluna 'Data'
        cols_to_clean_numeric = [col for col in (colunas_necessarias or []) if col != 'Data' and col in df.columns]
        for col in cols_to_clean_numeric:
            df[col] = df[col].apply(limpar_numero)
            # Após limpar_numero, converte para numérico e preenche NaNs com 0
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        logger.info(f"[DEBUG GSHEET] DataFrame após limpeza numérica com limpar_numero e fillna(0) ({nome_planilha} - {nome_aba}):\n{df.head()}\n{df.dtypes}")

        # Remove linhas sem todas as colunas obrigatórias preenchidas
        if colunas_necessarias is not None:
            df = df.dropna(subset=colunas_necessarias)

        if df.empty:
            raise ErroLeituraDadosError(
                f"Nenhum dado válido restante após limpeza na planilha '{nome_planilha}', aba '{nome_aba}'."
            )
        logger.info(f"[DEBUG GSHEET] DataFrame final antes do retorno ({nome_planilha} - {nome_aba}):\n{df.head()}\n{df.dtypes}")

        return df.reset_index(drop=True)

    except gspread.exceptions.SpreadsheetNotFound as e:
        raise PlanilhaNaoEncontradaError(
            f"Planilha '{nome_planilha}' não encontrada. Detalhe gspread: {e}"
        )
    except gspread.exceptions.WorksheetNotFound as e:
        raise AbaNaoEncontradaError(
            f"Aba '{nome_aba}' não encontrada na planilha '{nome_planilha}'. Detalhe gspread: {e}"
        )
    except gspread.exceptions.APIError as e:
        raise ErroLeituraDadosError(
            f"Erro na API do Google Sheets ao acessar dados. Detalhe: {e}"
        )
    except (ColunaNaoEncontradaError, ErroLeituraDadosError) as e_custom:
        raise e_custom
    except Exception as e:
        tb_str = traceback.format_exc()
        raise ErroLeituraDadosError(
            f"Erro inesperado ao extrair dados: {type(e).__name__} - {e}\nTraceback:\n{tb_str}"
        )


class GoogleSheetConnector:
    """
    Classe para conectar e interagir com o Google Sheets.
    """
    def __init__(self):
        self.config = load_config('app/config/global_config.json')
        
        # Carrega o caminho do arquivo de credenciais a partir de uma variável de ambiente.
        self.creds_path = os.getenv("GOOGLE_CREDS_PATH")
        if not self.creds_path:
            raise ValueError("A variável de ambiente GOOGLE_CREDS_PATH não está definida.")
        
        if not os.path.exists(self.creds_path):
            raise FileNotFoundError(f"Arquivo de credenciais não encontrado no caminho especificado por GOOGLE_CREDS_PATH: {self.creds_path}")
        
        self.scope = self.config['gsheet_scope']
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(self.creds_path, self.scope)
        self.client = gspread.authorize(self.creds)

    def get_data_from_sheet(self, spreadsheet_name: str, sheet_tab_name: str, colunas_necessarias=None, formato_data='%d/%m/%Y'):
        """
        Busca dados de uma planilha e aba específicas, usando a função extrair_dados_base.

        Args:
            spreadsheet_name (str): O nome da planilha no Google Sheets.
            sheet_tab_name (str): O nome da aba dentro da planilha.
            colunas_necessarias (list, optional): Lista de colunas obrigatórias. Defaults to None.
            formato_data (str, optional): Formato esperado da coluna 'Data'. Defaults to '%d/%m/%Y'.

        Returns:
            pd.DataFrame: DataFrame com os dados filtrados e limpos.
        """
        return extrair_dados_base(
            self.client,
            spreadsheet_name,
            sheet_tab_name,
            colunas_necessarias,
            formato_data
        )
