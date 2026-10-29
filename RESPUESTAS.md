# Preguntas de análisis

Repo: https://github.com/NyawToo/github-actions-stockguard

| Run | Evento | Commit | Resultado |
|---|---|---|---|
| [40805982725](https://github.com/NyawToo/github-actions-stockguard/actions/runs/40805982725) | push | `6a8ba14` estructura inicial | falló |
| [40806045029](https://github.com/NyawToo/github-actions-stockguard/actions/runs/40806045029) | push | `7aa18bf` pytest como módulo | pasó (5 pruebas) |
| [40806115701](https://github.com/NyawToo/github-actions-stockguard/actions/runs/40806115701) | push | `0f1a34d` fallo intencional | falló |
| [40806158150](https://github.com/NyawToo/github-actions-stockguard/actions/runs/40806158150) | push | `3fad9fc` restauración | pasó (5 pruebas) |
| [40806201045](https://github.com/NyawToo/github-actions-stockguard/actions/runs/40806201045) | pull_request | `f44de17` sobrestock | pasó (8 pruebas) |
| [40806241019](https://github.com/NyawToo/github-actions-stockguard/actions/runs/40806241019) | push | `e828c19` merge del PR #1 | pasó (8 pruebas) |
| [40806247714](https://github.com/NyawToo/github-actions-stockguard/actions/runs/40806247714) | workflow_dispatch | `e828c19` | pasó (8 pruebas) |

## 1. Una ejecución exitosa y una fallida

Tuve dos fallas distintas. La primera fue el push inicial (`6a8ba14`): el step `Ejecutar pruebas` terminó en rojo porque pytest no encontraba el paquete, con `ModuleNotFoundError: No module named 'src'`. Localmente el mismo comando pasaba, así que la diferencia era el entorno: en el runner `pytest` corre como script y no agrega la raíz del repo al `sys.path`. Lo resolví cambiando el step a `python -m pytest -v` (commit `7aa18bf`), que sí ejecuta desde la raíz.

La falla provocada a propósito fue en `0f1a34d`: cambié `test_stock_critico` para que esperara `"NORMAL"` con stock 7 y mínimo 20. Otra vez el step que decidió el resultado fue `Ejecutar pruebas`; `Validar sintaxis` e `Instalar dependencias` habían pasado.

## 2. Por qué pytest local no reemplaza a Actions

Porque mi máquina no es el runner. Local tengo Python 3.13.14, un `pytest` ya instalado y archivos que quizá nunca commiteé; el runner arranca con `ubuntu-latest`, Python 3.12.15 según el workflow, dependencias recién instaladas desde `requirements.txt` y solo lo que está en el repositorio. Eso ya me pasó acá: el mismo `pytest -v` daba 5 passed en Windows y falló en Linux por cómo se arma el `sys.path`. Además, en local nadie más ve el resultado; en Actions el resultado queda asociado a un commit y a un PR.

## 3. Riesgo de mergear sin esperar los checks

Que `main` quede roto y que el error lo descubra otro integrante cuando ya hizo `pull`. En este repo, si hubiera mergeado la rama con la prueba mal escrita, cualquier trabajo posterior habría partido de una base fallida y el primer run verde de cada uno habría sido una mentira. El check en el PR no evita el error: evita que el error llegue a la rama compartida.

## 4. Línea esencial del error

De la falla intencional:

```
E       AssertionError: assert 'CRITICO' == 'NORMAL'
```

Me alcanzó para diagnosticar sin abrir el archivo: la función devolvió `'CRITICO'` y la prueba esperaba `'NORMAL'`. Con stock 7 y mínimo 20, 7 es menor o igual al 50 % de 20, así que `CRITICO` es lo correcto y el error estaba en la expectativa de la prueba, no en `clasificar_stock`.

De la falla del primer push, la línea equivalente fue:

```
E   ModuleNotFoundError: No module named 'src'
```

Ahí el problema no era el código sino cómo se invocaba pytest.

## 5. `uses:` frente a `run:`

`uses:` llama a una acción publicada y versionada; GitHub descarga esa acción y ejecuta su código, y yo le paso parámetros con `with:`. En el workflow, `actions/checkout@v6` y `actions/setup-python@v5` hicieron trabajo que yo no escribí. `run:` ejecuta comandos de shell en el runner, con el sistema operativo que pedí en `runs-on`; por eso los comandos tienen que ser válidos para Linux. Los steps `Instalar dependencias`, `Validar sintaxis` y `Ejecutar pruebas` usan `run:` porque son comandos míos.

## 6. Qué aporta `${{ github.actor }}` en `run-name`

Es el usuario que disparó la ejecución. En las siete corridas de la tabla el título quedó como `CI ejecutado por NyawToo`, porque todas las disparé yo. En un equipo de tres sirve para separar ejecuciones del mismo commit: si dos integrantes lanzan `Run workflow` sobre `main`, el nombre distingue quién hizo qué sin abrir cada log. Es lo que la guía plantea como evidencia de participación individual.

## 7. Si el workflow pasa pero Docker falla localmente

No significa que Actions no sirva; significa que verifiqué otra cosa. El workflow valida que el código Python compile (`compileall src tests`), que las dependencias declaradas se instalen y que las 8 pruebas unitarias pasen. No levanta contenedores, no valida `docker-compose.yml`, no habla con Kafka ni con Spark y no prueba integración entre servicios. Un error de puerto, una imagen mal taggeada o una variable de entorno faltante pasan perfectamente por este CI.

## 8. Tres checks para mi variante de RapidGo

1. `pytest` sobre la regla de negocio de la variante, por ejemplo `clasificar_cumplimiento(tiempo_real, tiempo_objetivo)` con casos normal, límite e inválido. Evita que alguien cambie un umbral de SLA y rompa la clasificación sin darse cuenta.
2. `docker compose config --quiet`. Evita mergear un `docker-compose.yml` con indentación rota o una referencia a un servicio que no existe, que es el error que aparece recién cuando alguien intenta levantar el entorno.
3. Validación de esquema de los eventos JSON que produce el producer (con `jsonschema` y un archivo de ejemplo). Evita que un campo renombrado rompa el consumidor o el job de Spark en la siguiente etapa.

## 9. Cuál implementar primero

El de `pytest` sobre la regla de negocio. Es el único que protege la decisión central de la variante, corre en segundos y no necesita infraestructura. Los otros dos son baratos, pero protegen configuración; si la regla está mal, el entorno levanta igual.

## 10. Qué prueba sería demasiado costosa o frágil

Levantar Kafka + Spark + Airflow y esperar a que el producer mande datos durante varios minutos en cada push. Es lento, consume minutos, depende de servicios externos y falla por razones que no tienen que ver con el cambio. La validaría aparte: una ejecución manual con `workflow_dispatch` antes de la entrega, o un workflow programado con `schedule` que corra de noche, y evidencia local del equipo para el resto de las semanas.
