import pandas as pd
import re

def clean_text(text: str) -> str:
    """
    Limpa um texto, removendo espaços extras e caracteres especiais.
    """
    text = re.sub(r'\s+', ' ', text) # Remove espaços múltiplos
    text = text.strip()
    return text

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Realiza uma limpeza básica em um DataFrame.
    - Remove linhas e colunas completamente vazias.
    - Converte nomes de colunas para snake_case.
    """
    # Remove linhas e colunas vazias
    df.dropna(how='all', inplace=True)
    df.dropna(axis=1, how='all', inplace=True)

    # Limpa nomes das colunas
    new_columns = {}
    for col in df.columns:
        new_col = col.strip().lower().replace(' ', '_')
        new_columns[col] = new_col
    df.rename(columns=new_columns, inplace=True)
    
    return df

def limpar_numero(valor):
    """
    Converte para float, tratando diferentes formatos numéricos (BR/US) e símbolos.
    Retorna None se não for possível converter.
    """
    if pd.isna(valor) or valor == '':
        return None
    s_valor = str(valor).strip()
    if not s_valor:
        return None

    # Remove símbolos de moeda e outros caracteres não numéricos, exceto '.' e ','
    cleaned_value = re.sub(r'[^\d.,]+', '', s_valor)

    # Detecta o separador decimal: se a última ocorrência for vírgula, é formato BR
    if ',' in cleaned_value and '.' in cleaned_value:
        if cleaned_value.rfind(',') > cleaned_value.rfind('.'):
            # Formato Brasileiro: remove pontos de milhar, troca vírgula por ponto decimal
            cleaned_value = cleaned_value.replace('.', '')
            cleaned_value = cleaned_value.replace(',', '.')
        else:
            # Formato Americano: remove vírgulas de milhar
            cleaned_value = cleaned_value.replace(',', '')
    elif ',' in cleaned_value:
        # Apenas vírgula presente, assume que é separador decimal (formato BR)
        cleaned_value = cleaned_value.replace(',', '.')
    # Se apenas ponto presente, assume que é separador decimal (formato US), não faz nada

    try:
        return round(float(cleaned_value), 2)
    except ValueError:
        return None

def limpar_porcentagem(valor):
    """
    Converte porcentagem para float, tratando diferentes formatos e símbolos.
    Retorna None se não for possível.
    """
    if pd.isna(valor) or valor == '':
        return None
    s_valor = str(valor).strip().replace('%', '')
    
    try:
        # Tenta converter diretamente (assume ponto como decimal)
        return round(float(s_valor), 2)
    except ValueError:
        # Se falhar, tenta trocar vírgula por ponto e converter
        s_valor = s_valor.replace(',', '.')
        try:
            return round(float(s_valor), 2)
        except ValueError:
            return None