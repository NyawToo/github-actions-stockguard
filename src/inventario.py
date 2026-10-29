def clasificar_stock(stock_actual: int, stock_minimo: int) -> str:
    if stock_actual < 0:
        raise ValueError("El stock actual no puede ser negativo")
    if stock_minimo <= 0:
        raise ValueError("El stock minimo debe ser mayor que cero")

    if stock_actual == 0:
        return "AGOTADO"

    if stock_actual <= stock_minimo * 0.5:
        return "CRITICO"
    if stock_actual <= stock_minimo:
        return "BAJO"
    return "NORMAL"


def detectar_sobrestock(stock_actual: int, stock_maximo: int) -> str:
    if stock_actual < 0:
        raise ValueError("El stock actual no puede ser negativo")
    if stock_maximo <= 0:
        raise ValueError("El stock maximo debe ser mayor que cero")

    if stock_actual > stock_maximo:
        return "SOBRESTOCK"
    return "ADECUADO"
