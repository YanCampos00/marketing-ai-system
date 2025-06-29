def limpar_numero(valor):
    """
    Converte uma string numérica (potencialmente com 'R$', separador de milhar ',',
    e separador decimal '.') para float ou int.
    - Remove 'R$'
    - Remove ',' (assumido como separador de milhar)
    - '.' é tratado como separador decimal.
    """
    if valor is None:
        return None
    if isinstance(valor, (int, float)):
        # Se já for int ou float, retorna, garantindo tipo correto
        return float(valor) if isinstance(valor, float) else int(valor)

    if not isinstance(valor, str):
        try:
            # Tenta converter diretamente se não for string
            temp_val = float(valor)
            return int(temp_val) if temp_val.is_integer() else temp_val
        except (ValueError, TypeError):
            return None

    s = str(valor).strip()
    s = s.replace("R$", "").strip() # Remove 'R$' e espaços adjacentes
    s = s.replace(",", "")         # Remove ',' (assumido como separador de milhar)

    if not s: # String vazia após limpeza
        return None

    try:
        f = float(s) # O '.' já é o decimal correto
        return int(f) if f.is_integer() else f
    except ValueError:
        return None


def limpar_porcentagem(valor_str):
    """
    Converte uma string de porcentagem (ex: "1,234.56%" ou "0.56%") para float (ex: 0.0056).
    Assume ',' como separador de milhar (se houver) e '.' como decimal.
    """
    if valor_str is None:
        return None
    if isinstance(valor_str, (int, float)):
        return float(valor_str)

    if not isinstance(valor_str, str):
        try:
            return float(valor_str)
        except (ValueError, TypeError):
            return None

    s = valor_str.strip()
    s = s.replace("%", "").strip()   # Remove o símbolo de porcentagem
    s = s.replace(",", "")           # Remove ',' (assumido como separador de milhar)
    # O '.' já é o decimal correto

    if not s: # String vazia após limpeza
        return None

    try:
        return float(s) / 100.0
    except ValueError:
        return None
