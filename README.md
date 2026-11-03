# ConsultaVoto — Proyecto de portafolio QA

> ⚠️ **Proyecto ficticio de demostración.** ConsultaVoto no es un sitio oficial ni está conectado a ningún registro electoral real. Todos los nombres, cédulas, puestos y mesas son datos inventados.

Aplicación web full stack de consulta electoral, construida como **sistema bajo prueba** para mostrar buenas prácticas de Quality Engineering y automatización de pruebas en varios niveles: unitario, API, BDD y E2E.

## Funcionalidad

- El usuario ingresa su número de cédula.
- La app muestra su **lugar de votación**: puesto, dirección, ciudad, departamento y mesa.
- Si el ciudadano fue designado **jurado de votación**, muestra además su asignación: rol, puesto y mesa de servicio.
- Maneja los casos de **campo vacío**, **formato inválido** y **cédula no encontrada**.

## Stack

| Capa | Tecnología |
|------|------------|
| Backend | Python 3.11, Django 5.2 LTS, Django REST Framework |
| Base de datos | MySQL 8.0 |
| Frontend | React + Vite |
| Pruebas unitarias / integración | pytest + pytest-django |
| Pruebas de API | pytest + requests |
| BDD | pytest-bdd (Gherkin en español) |
| E2E / UI | Playwright para Python |
| CI | GitHub Actions |

## Modelo de datos

Definido en [`backend/apps/consultas/models.py`](backend/apps/consultas/models.py).

```mermaid
erDiagram
    DEPARTAMENTO ||--o{ CIUDAD : "tiene"
    CIUDAD ||--o{ PUESTO_VOTACION : "tiene"
    PUESTO_VOTACION ||--o{ MESA : "tiene"
    MESA ||--o{ PERSONA : "vota en"
    PERSONA ||--o| DESIGNACION_JURADO : "puede tener"
    MESA ||--o{ DESIGNACION_JURADO : "sirve en"

    DEPARTAMENTO {
        string cod_departamento PK "2 caracteres"
        string nombre
    }
    CIUDAD {
        string cod_ciudad PK "5 caracteres"
        string nombre
        string cod_departamento FK
    }
    PUESTO_VOTACION {
        string cod_puesto PK "hasta 10 caracteres"
        string nombre
        string direccion
        string cod_ciudad FK
    }
    MESA {
        bigint cod_mesa PK
        smallint numero "único por puesto"
        string cod_puesto FK
    }
    PERSONA {
        string cedula PK "solo dígitos, hasta 10"
        string primer_nombre
        string segundo_nombre "opcional"
        string primer_apellido
        string segundo_apellido "opcional"
        string genero "F, M u O"
        date fecha_nacimiento
        bigint cod_mesa FK "mesa donde vota"
    }
    DESIGNACION_JURADO {
        bigint cod_designacion PK
        string cedula FK "única: una designación por persona"
        bigint cod_mesa_servicio FK "mesa donde sirve"
        string rol "TITULAR o REMANENTE"
    }
```

**Reglas de negocio reflejadas en el modelo**

| Regla | Cómo se implementa |
|-------|--------------------|
| Una persona sin designación es **solo votante** | `DesignacionJurado` es opcional (relación 1 a 0..1 con `Persona`) |
| Un jurado puede servir en una mesa o puesto **distinto** a donde vota | `Persona.mesa` y `DesignacionJurado.mesa_servicio` son relaciones independientes |
| El puesto y la dirección de servicio no se duplican | Se obtienen a través de `mesa_servicio.puesto` |
| No hay dos mesas con el mismo número en un puesto | Restricción `mesa_unica_por_puesto` |
| La cédula admite valores de 10 dígitos sin desbordamiento | `cedula` es texto (`CharField(max_length=10)`), no entero |
| La edad nunca queda desactualizada | No se almacena: se calcula desde `fecha_nacimiento` (`calcular_edad(fecha_referencia)`) |
| Los datos de referencia no se borran en cascada | Las relaciones usan `PROTECT`; solo la designación se elimina con su persona |

### Datos de demostración

El fixture [`datos_demo.json`](backend/apps/consultas/fixtures/datos_demo.json) usa la **división política real** de Colombia (33 departamentos con códigos DIVIPOLA del DANE) y datos **inventados** para puestos, mesas y personas. Las cédulas siguen el formato colombiano, de 7 a 10 dígitos. Cada persona cubre un escenario de prueba: solo votante, jurado en la misma mesa, jurado en otra mesa del mismo puesto y jurado en otro puesto, además de casos borde (sin segundo nombre o apellido, nacimiento un 29 de febrero, cédulas antiguas).

## API

`POST /api/consulta/` con `{"cedula": "1098765432"}`. La cédula va en el cuerpo y no en la URL, para que no quede registrada en logs ni historiales.

```json
{
  "ciudadano": { "cedula": "1098765432", "nombre_completo": "Carlos Andrés Martínez", "edad": 36 },
  "lugar_votacion": { "mesa": 18, "puesto": "Colegio Cívico La Esperanza", "direccion": "Calle 48 # 65-20", "ciudad": "Medellín", "departamento": "Antioquia" },
  "jurado": { "rol": "TITULAR", "rol_display": "Jurado titular", "mesa": 18, "puesto": "Colegio Cívico La Esperanza", "direccion": "Calle 48 # 65-20", "ciudad": "Medellín", "departamento": "Antioquia", "misma_mesa": true }
}
```

`jurado` es `null` cuando la persona solo vota. Todos los errores responden `{"codigo", "mensaje"}`:

| HTTP | `codigo` | Cuándo |
|------|----------|--------|
| 400 | `CEDULA_REQUERIDA` | Cédula vacía o ausente |
| 400 | `CEDULA_FORMATO_INVALIDO` | No son de 6 a 10 dígitos sin 0 inicial (letras, puntos, comas, espacios internos) |
| 404 | `CEDULA_NO_ENCONTRADA` | Cédula no registrada |
| 400 / 415 | `SOLICITUD_INVALIDA` | El cuerpo no es un objeto JSON válido |
| 405 | `METODO_NO_PERMITIDO` | Método distinto de POST |
| 429 | `DEMASIADAS_CONSULTAS` | Más de 30 consultas por minuto desde la misma IP (configurable con `CONSULTA_LIMITE_POR_MINUTO`) |

## Estrategia de pruebas

```
            ┌───────────┐
            │    E2E    │  Playwright + Page Object Model
            ├───────────┤
            │    BDD    │  pytest-bdd, escenarios de negocio en Gherkin
            ├───────────┤
            │    API    │  Black-box contra la API REST
            ├───────────┤
            │ Unitarias │  White-box de validadores y servicios
            └───────────┘
```

- **Page Object Model** compartido entre E2E y BDD (`tests/support/pages/`).
- **`conftest.py` por nivel** para aislar fixtures.
- **Datos de prueba externos** en `tests/data/`, nunca quemados en los tests.
- **Markers** (`api`, `bdd`, `e2e`, `smoke`, `regression`) para ejecutar suites selectivas.

## Estructura del proyecto

```
.
├── .github/workflows/ci.yml   # Pipeline de CI (placeholder)
├── backend/                   # API Django + DRF
│   ├── config/                # Proyecto Django y settings por entorno
│   ├── apps/consultas/        # App de dominio: modelos, admin, validadores, servicios, vistas
│   │   ├── migrations/        # Migraciones de la base de datos
│   │   └── fixtures/          # Datos de demostración (datos_demo.json)
│   ├── manage.py
│   ├── pytest.ini             # Configuración de pytest-django (settings de test)
│   └── tests/                 # Pruebas white-box (pytest-django)
├── frontend/                  # React + Vite
│   └── src/
│       ├── pages/             # Una página por pantalla del diseño
│       ├── components/        # layout/, common/, consulta/, resultado/
│       ├── services/          # Cliente de la API
│       ├── hooks/
│       ├── utils/
│       └── styles/            # Tokens de diseño y estilos globales
├── tests/                     # Pruebas black-box contra la app en ejecución
│   ├── data/                  # Datos de prueba (JSON)
│   ├── support/               # Cliente de API, configuración y Page Objects
│   ├── api/                   # Pruebas de API
│   ├── bdd/                   # features/ (Gherkin) + step_defs/
│   └── e2e/                   # Pruebas de UI con Playwright
├── pytest.ini                 # Configuración y markers de las pruebas black-box
└── .env.example               # Variables de entorno requeridas
```

## Estado del proyecto

| Componente | Estado |
|------------|--------|
| Estructura del monorepo | ✅ |
| Modelo de datos y migración inicial | ✅ |
| Settings de Django por entorno (`local`, `test`) | ✅ |
| Datos de demostración (fixture) | ✅ |
| Admin de Django para revisar los datos | ✅ |
| API REST de consulta (`POST /api/consulta/`) | ✅ |
| Pruebas white-box del backend (pytest-django, 77 pruebas) | ✅ |
| Pruebas black-box de la API (pytest + requests, 59 pruebas) | ✅ |
| Pruebas BDD (pytest-bdd, Gherkin en español, 14 casos contra la API) | ✅ |
| Frontend React | 🚧 Pendiente |
| Pruebas BDD contra la interfaz y E2E | 🚧 Pendiente |
| Pipeline de CI | 🚧 Placeholder |

## Ejecución

### Requisitos

- Python 3.11 (Django 5.2 LTS; Django 6 exige Python 3.12+)
- MySQL 8.0 en local
- Windows / PowerShell en los ejemplos. En Linux o macOS el entorno se activa con `source .venv/bin/activate`.

### 1. Entorno virtual y dependencias

Un solo entorno en la raíz para el backend y las pruebas:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt -r tests/requirements.txt
python -m playwright install        # navegadores para las pruebas E2E
```

### 2. Base de datos

Con un usuario administrador de MySQL, crea la base y un usuario propio del proyecto. `test_registraduria` es la base temporal que pytest-django crea y borra en cada corrida de pruebas:

```sql
CREATE DATABASE registraduria CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
CREATE USER 'consultavoto_app'@'localhost' IDENTIFIED BY '<contraseña>';
GRANT ALL PRIVILEGES ON registraduria.* TO 'consultavoto_app'@'localhost';
GRANT ALL PRIVILEGES ON test_registraduria.* TO 'consultavoto_app'@'localhost';
```

### 3. Variables de entorno

Copia la plantilla y completa los valores. El archivo `.env` nunca se sube al repositorio:

```powershell
Copy-Item .env.example .env
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Obligatorias: `DJANGO_SECRET_KEY`, `MYSQL_DATABASE`, `MYSQL_USER` y `MYSQL_PASSWORD`. Las demás tienen valores por defecto para desarrollo local (ver comentarios en [`.env.example`](.env.example)).

### 4. Migraciones, datos de demostración y superusuario

```powershell
cd backend
python manage.py migrate
python manage.py loaddata datos_demo
python manage.py createsuperuser
```

### 5. Levantar el backend

```powershell
python manage.py runserver
```

Admin en http://127.0.0.1:8000/admin/: muestra departamentos, ciudades, puestos, mesas, personas (con filtro "es jurado") y designaciones de jurado.

Probar la API desde PowerShell (con el servidor corriendo):

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/consulta/ `
  -ContentType 'application/json' -Body '{"cedula": "1098765432"}' | ConvertTo-Json -Depth 5
```

### 6. Pruebas del backend

```powershell
cd backend
pytest
```

pytest-django crea la base `test_registraduria`, carga los datos de demostración y la borra al terminar.

### 7. Pruebas black-box de la API y BDD

Se ejecutan contra el servidor en marcha y con los datos de demostración cargados. La suite hace unas 60 peticiones seguidas, así que el servidor se levanta con un límite de consultas alto. En una terminal:

```powershell
$env:CONSULTA_LIMITE_POR_MINUTO = "1000"
cd backend
python manage.py runserver
```

En otra terminal, desde la raíz del repositorio:

```powershell
pytest tests/api            # pruebas de la API
pytest tests/bdd            # escenarios de negocio en Gherkin
pytest tests/api tests/bdd -m smoke   # subconjunto crítico de ambas
```

Los escenarios BDD están en [`tests/bdd/features/`](tests/bdd/features). Están escritos en lenguaje de negocio, así que cuando exista el frontend se ejecutarán también contra la interfaz.

La URL de la API se toma de `API_BASE_URL` en el `.env` (por defecto `http://127.0.0.1:8000`). Si el servidor no está levantado, la corrida se detiene con instrucciones. Los casos y las respuestas esperadas están en [`tests/data/`](tests/data).

### Pendiente

- Levantar el frontend
- Steps de interfaz para los features BDD, pruebas E2E y reportes

## Aviso

Este repositorio es un proyecto de portafolio con fines educativos. No representa a ninguna entidad oficial y no debe usarse para consultar información electoral real.
