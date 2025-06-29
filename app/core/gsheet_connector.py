import pandas as pd
import gspread
from app.utils.custom_exceptions import (
    PlanilhaNaoEncontradaError,
    AbaNaoEncontradaError,
    ColunaNaoEncontradaError,
    ErroLeituraDadosError
)
from app.utils.data_cleaners import limpar_numero
from datetime import datetime
import traceback

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
        if not all_data:
            raise ErroLeituraDadosError(
                f"Nenhum dado encontrado na planilha '{nome_planilha}', aba '{nome_aba}'."
            )
        df = pd.DataFrame(all_data)

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
        for col in (colunas_necessarias or []):
            if col != 'Data' and col in df.columns:
                df[col] = df[col].apply(limpar_numero)
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Remove linhas sem todas as colunas obrigatórias preenchidas
        if colunas_necessarias is not None:
            df = df.dropna(subset=colunas_necessarias)

        if df.empty:
            raise ErroLeituraDadosError(
                f"Nenhum dado válido restante após limpeza na planilha '{nome_planilha}', aba '{nome_aba}'."
            )

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
