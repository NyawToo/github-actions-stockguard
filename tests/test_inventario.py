import pytest

from src.inventario import clasificar_stock, detectar_sobrestock


def test_stock_agotado():
    assert clasificar_stock(0, 20) == "AGOTADO"


def test_stock_critico():
    assert clasificar_stock(7, 20) == "CRITICO"


def test_stock_bajo():
    assert clasificar_stock(15, 20) == "BAJO"


def test_stock_normal():
    assert clasificar_stock(30, 20) == "NORMAL"


def test_stock_invalido():
    with pytest.raises(ValueError):
        clasificar_stock(-2, 20)


def test_sobrestock_detectado():
    assert detectar_sobrestock(25, 20) == "SOBRESTOCK"


def test_sobrestock_en_el_limite():
    assert detectar_sobrestock(20, 20) == "ADECUADO"


def test_sobrestock_maximo_invalido():
    with pytest.raises(ValueError):
        detectar_sobrestock(10, 0)
