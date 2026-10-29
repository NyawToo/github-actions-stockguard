# github-actions-stockguard

Práctica autónoma de GitHub Actions para la línea de Big Data: CI con Python, pytest y Pull Requests.

StockGuard clasifica el riesgo de inventario de un producto a partir del stock disponible y del stock mínimo requerido.

| Condición | Resultado |
|---|---|
| stock actual = 0 | `AGOTADO` |
| stock actual <= 50 % del mínimo | `CRITICO` |
| stock actual <= mínimo | `BAJO` |
| cualquier otro caso | `NORMAL` |
| stock actual > stock máximo | `SOBRESTOCK` |

Los valores negativos y un stock mínimo menor o igual a cero lanzan `ValueError`.

## Ejecutar las pruebas en local

```bash
python -m pip install -r requirements.txt
pytest -v
```

## CI

El workflow `.github/workflows/ci.yml` se ejecuta en `push` y `pull_request` sobre `main`, y también de forma manual con `workflow_dispatch`. Instala dependencias, valida sintaxis con `compileall` y corre `pytest -v`.
