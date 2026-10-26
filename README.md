# SplitMate API — Proyecto base del alumno (Unidad 1)

SplitMate es una API REST para dividir gastos de un viaje en grupo y calcular quién le paga a quién. La creación y consulta de viajes ya funciona, igual que el borrado de gastos (`DELETE`), que te sirve como ejemplo resuelto. Tu trabajo tiene dos partes: el **taller guiado** y el **reto autónomo**.

## Primeros pasos

```bash
uv sync                     # instala Python 3.13 y las dependencias exactas de uv.lock
uv run pytest -v            # al inicio: 2 tests en verde, el resto en rojo
uv run uvicorn app.main:app --reload    # consola en http://127.0.0.1:8000, Swagger en /docs
SEED_DEMO_DATA=true uv run uvicorn app.main:app --reload   # arranca con un viaje de ejemplo
```

Antes de entregar corre siempre `uv run ruff check .`, `uv run ruff format --check .` y `uv run pytest -v`.

## Estructura de tests

| Archivo | Qué contiene | Estado inicial |
| :--- | :--- | :--- |
| `tests/conftest.py` | Fixtures oficiales `client`, `create_trip` y `add_expense`; bloquean la red y crean un almacén limpio por test | No lo modifiques |
| `tests/test_demo.py` | 2 tests de la demo | Verde |
| `tests/test_workshop.py` | Tests del taller guiado (`split_evenly`, `add_expense`, `calculate_settlements`) | Rojo |
| `tests/test_challenge.py` | Tests **públicos** del reto PATCH (una muestra) | Rojo |
| `tests/student/test_my_scenarios.py` | Tus tests propios (2 plantillas con `pytest.fail`) | Rojo |

Los archivos oficiales (`conftest.py`, `test_demo.py`, `test_workshop.py`, `test_challenge.py`) y `.github/workflows/ci.yml` no se modifican. El calificador usa siempre su propia copia y reporta cualquier cambio como sospecha de integridad.

## Parte 1. Taller guiado (60 minutos)

Trabaja en la raíz de tu repositorio y sigue el codelab publicado en el material de la unidad. Implementarás, con el código guiado paso a paso:

1. `split_evenly` en `app/money.py`: reparto de un monto al centavo con `Decimal`.
2. `_check_expense_rules` y `add_expense` en `app/store.py`: reglas de dominio (moneda del viaje y participantes).
3. `calculate_settlements` en `app/store.py`: saldos netos exactos y transferencias con el algoritmo greedy.

Al terminar, `tests/test_demo.py` y `tests/test_workshop.py` quedan en verde.

## Parte 2. Reto autónomo: editar un gasto con PATCH

Un gasto mal registrado hoy solo se puede borrar y volver a crear, lo que cambia su `id` y su fecha de creación. Implementa la **actualización parcial** de un gasto. Calcula entre 2 y 3 horas para el reto, más 45 minutos para tus tests propios y 45 minutos para los documentos. No hay código guiado: diseña tú el esquema, el método del almacén y la ruta.

### Contrato

`PATCH /api/v1/trips/{trip_id}/expenses/{expense_id}`

**Cuerpo**: un objeto JSON con **uno o más** de estos campos y ningún otro:

| Campo | Reglas (las mismas que al crear el gasto) |
| :--- | :--- |
| `description` | texto; se recortan espacios repetidos; de 3 a 120 caracteres |
| `amount` | número o texto (`25`, `25.5`, `"25.50"`); mayor que 0, como máximo `100000.00`, como máximo 2 decimales |
| `currency` | `USD`, `EUR`, `GTQ` o `MXN`, sin importar mayúsculas ni espacios |
| `category` | `food`, `transport`, `lodging`, `activities` u `other` |
| `paid_by` | nombre que se normaliza igual que al crear (forma Unicode NFC, espacios y mayúsculas iniciales); se rechazan caracteres de control o invisibles |
| `split_among` | lista de 1 a 20 nombres normalizados y sin repetidos |

**Semántica**

1. Solo cambian los campos enviados. Los demás conservan su valor.
2. El gasto resultante (lo existente combinado con lo nuevo) debe cumplir las reglas de dominio del viaje: misma moneda que el viaje y pagador y beneficiarios que pertenezcan al viaje.
3. La operación es **atómica**: si responde con error, el gasto queda exactamente como estaba.
4. `id`, `trip_id` y `created_at` no cambian. `updated_at` vale `null` al crear un gasto y, tras un PATCH exitoso, guarda la fecha y hora UTC de la última modificación.
5. El gasto conserva su posición en `GET /api/v1/trips/{trip_id}/expenses`.
6. Todo lo derivado se recalcula: `shares` del gasto (centavos sobrantes a los primeros nombres en orden alfabético sin distinguir acentos, igual que al crear), `total_spent` y `expense_count` del viaje y `GET /settlements`.
7. Enviar dos veces el mismo PATCH deja el gasto igual (salvo `updated_at`).

**Respuestas**

| Situación | Código | `error_code` |
| :--- | :---: | :--- |
| Actualización válida; el cuerpo es el gasto completo (mismo formato que `POST`) | `200` | (sin error) |
| `trip_id` o `expense_id` de más de 64 caracteres (como en las demás rutas), cuerpo vacío `{}`, cuerpo que no es un objeto, campo fuera de la tabla (por ejemplo `id`, `trip_id`, `created_at`, `updated_at`, `shares`), campo con `null` o valor que viola las reglas | `422` | `VALIDATION_ERROR` |
| El viaje no existe | `404` | `TRIP_NOT_FOUND` |
| El gasto no existe **en ese viaje** (incluye un gasto borrado o el `id` de un gasto de otro viaje) | `404` | `EXPENSE_NOT_FOUND` |
| La moneda resultante no es la del viaje | `400` | `CURRENCY_MISMATCH` |
| El pagador o algún beneficiario resultante no pertenece al viaje | `400` | `INVALID_PARTICIPANT` |

**Orden de evaluación**: FastAPI valida el cuerpo primero (422). Después se revisa el viaje (404 `TRIP_NOT_FOUND`), luego el gasto (404 `EXPENSE_NOT_FOUND`), luego la moneda (400 `CURRENCY_MISMATCH`) y por último los participantes (400 `INVALID_PARTICIPANT`).

**Restricciones de arquitectura** (ver `AGENTS.md`): el dinero se maneja con `Decimal` de punta a punta; `app/store.py` no importa nada de FastAPI y lanza excepciones de dominio; el esquema de entrada del PATCH es un DTO propio, distinto de `ExpenseCreate` y de `ExpenseResponse`.

### Tus tests propios

Tus tests propios suman si pasan contra la solución de referencia y detectan mutantes que la suite pública no detecta (errores sembrados en el reto). Reescribir un test público no suma. Reemplaza las 2 plantillas de `tests/student/test_my_scenarios.py` por al menos 2 tests con nombres que digan qué verifican. Usa los fixtures oficiales y no crees `conftest.py` en `tests/student/`.

### Decisiones y checklist

Responde `ARCHITECTURE_DECISIONS.md` (incluye ampliar `AGENTS.md` con una regla propia y la declaración de uso de IA) y marca con criterio `SECURITY_AND_QUALITY.md`.

## Cómo se califica (100 puntos)

| Componente | Puntos | Cómo se mide |
| :--- | ---: | :--- |
| Taller guiado | 20 | `tests/test_workshop.py`, proporcional |
| Reto, tests públicos | 10 | `tests/test_challenge.py`, proporcional |
| Reto, tests ocultos | 30 | tests ocultos, proporcional |
| Tests propios | 15 | pasan contra la referencia y detectan mutantes que la suite pública no detecta (los errores sembrados se agrupan por concepto: 2 conceptos distintos = completo, 1 = mitad) |
| ADR y checklist | 15 | revisión manual: ADR 10, checklist 2, sección propia de `AGENTS.md` 2 y declaración de uso de IA 1 |
| Calidad e integridad | 10 | `ruff check` y `ruff format --check` limpios (5) + sin sospechas de integridad (5) |
| **Total** | **100** | |

**La nota no sale de tu CI.** El workflow de GitHub Actions solo te da retroalimentación. El calificador del curso calcula la nota sobre una copia limpia del proyecto: toma tu `app/`, tus tests propios y tus documentos, y corre los tests oficiales más un conjunto de **tests ocultos** del reto con otros datos y más casos borde. Te lo decimos de frente para que no pierdas tiempo: memorizar las respuestas de `test_challenge.py` o detectar si el código corre bajo pytest no sirve, y además se reporta. Implementa el contrato completo y pruébalo con tus propios casos.

Se marca como sospecha de integridad: modificar tests oficiales o el workflow, crear `conftest.py` en `tests/student/`, y que `app/` mencione `pytest`, `PYTEST_CURRENT_TEST`, `sys._getframe`, `inspect.stack`, `builtins`, `__import__` o lea archivos de `tests/`.

<!-- texto-escaner:inicio (generado por scripts/texto_escaner.py; no editar a mano) -->

### Qué marca el escáner del calificador

El calificador revisa tu código y tus tests antes de correrlos. Si encuentra algo de esta lista, tu nota queda **retenida** hasta que el docente la revise: no pierdes puntos automáticamente, pero tampoco se publica. Nada de esto hace falta para resolver los retos.

**Por qué existe.** Tus tests corren en la misma máquina que los tests ocultos. Lo que se marca es lo que permitiría leer esos tests, cambiar el resultado de las pruebas o salir a internet desde el calificador.

**En este proyecto (Python).**

- En `app/` puedes importar: `__future__`, `abc`, `app`, `base64`, `bisect`, `collections`, `contextlib`, `copy`, `dataclasses`, `datetime`, `decimal`, `enum`, `fastapi`, `functools`, `google.genai`, `hashlib`, `heapq`, `hmac`, `html`, `itertools`, `json`, `jwt`, `logging`, `math`, `operator`, `os` (solo `os.environ` y `os.getenv`), `pydantic`, `pydantic_settings`, `re`, `secrets`, `sqlalchemy`, `sqlmodel`, `starlette`, `statistics`, `string`, `textwrap`, `threading`, `time`, `typing`, `typing_extensions`, `unicodedata`, `uuid` y `zoneinfo`.
- En `tests/student/` puedes importar: `__future__`, `abc`, `app`, `asyncio`, `base64`, `collections`, `concurrent.futures`, `contextlib`, `copy`, `dataclasses`, `datetime`, `decimal`, `enum`, `fastapi`, `functools`, `hashlib`, `hmac`, `itertools`, `json`, `jwt`, `math`, `operator`, `pydantic`, `pytest`, `random`, `re`, `sqlalchemy`, `sqlmodel`, `starlette`, `statistics`, `string`, `tests`, `textwrap`, `threading`, `time`, `typing`, `unicodedata`, `unittest` (incluido `unittest.mock`), `uuid` y `zoneinfo`.
- Sí puedes: `chr(0x200B)` y cualquier `chr`, unir textos (`"a" + "b"`, f-strings), `vars(objeto)` para comparar (`assert vars(x) == {...}`), `mock.patch("app.…")`, `mock.patch.dict("os.environ", {...})`, `monkeypatch.setenv`, `random` y `functools.singledispatch`.
- Se marca: `eval`, `exec`, `compile`, `open`, `input`, `breakpoint`, `globals`, `locals`, `__import__`, `memoryview`; `vars()` sin argumentos o usado para indexar, recorrer o guardar; `getattr`/`setattr`/`hasattr`/`delattr` con un nombre que no es un texto fijo (salvo sobre `self` o `cls`) o con un nombre prohibido; `operator.attrgetter`/`methodcaller` con nombres calculados o prohibidos; atributos mágicos (`__dict__`, `__globals__`, `__subclasses__`…, salvo `__name__`, `__init__`, `__class__` y `__all__`); acceso a módulos del sistema a través de otro objeto (`.sys`, `.builtins`, `.subprocess`, `.inspect`, `.io`, `.os` fuera de `environ`/`getenv`…); frames (`_getframe`, `f_back`…); procesos y archivos (`system`, `popen`, `fork`, `exec*`, `create_subprocess_exec`, `read_text`, `write_text`, `listdir`, `chdir`, `unlink`…); variables de entorno leídas con un nombre calculado o recorridas (en `app/`); textos, aunque estén armados por partes, que mencionen `pytest`, `junit`, `AWA_`, `site-packages`, `builtins` o atributos mágicos (en `app/`). En tests, además: rutas de módulos no permitidos escritas como texto (`mock.patch("subprocess.run")`, `"_pytest…"`), hooks de pytest (`def pytest_…`), `pytest_plugins`, `request.config.pluginmanager`/`hook`, y los internos de `mock.patch` y `monkeypatch` (`temp_original`, `getter`, `_setattr`); un `conftest.py` propio.

**En todos los proyectos** se marca además: modificar o borrar archivos oficiales, agregar archivos fuera de tus carpetas, enlaces simbólicos, y archivos como `sitecustomize.py`, `pytest.ini`, `init.gradle` o `.npmrc`. Y tus tests deben dar siempre el mismo resultado: un test que falla al azar no cuenta.

<!-- texto-escaner:fin -->

## Uso de asistentes de IA

Puedes usar asistentes de IA. Eres responsable de todo lo que entregas: revisa que el código cumpla el contrato y `AGENTS.md`, y declara cómo los usaste en `ARCHITECTURE_DECISIONS.md`.
