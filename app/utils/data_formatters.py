import pandas as pd

def formatar_markdown_consolidado(df: pd.DataFrame, titulo: str) -> str:
    """
    Formata um DataFrame (como KPIs ou comparativos) em uma tabela Markdown com um título.

    Args:
        df (pd.DataFrame): O DataFrame a ser formatado.
        titulo (str): O título da tabela.

    Returns:
        str: A tabela formatada em Markdown.
    """
    if df.empty:
        return f"### {titulo}\n\nNenhum dado disponível.\n\n"

    # Aplica formatação de 2 casas decimais para colunas numéricas
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].round(2)

    # Garante que o índice (que pode ser 'Google Ads', 'Meta Ads') seja incluído na tabela
    markdown_table = df.to_markdown(index=True, tablefmt="pipe")
    
    return f"### {titulo}\n\n{markdown_table}\n\n"

