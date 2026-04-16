# Blacklist API - Entrega 1

Microservicio para gestionar la lista negra global de emails de la organizacion. Permite agregar emails a la lista negra y consultar si un email esta bloqueado.

## Tech Stack

- Python 3.13
- Flask 2.3.3
- Flask-SQLAlchemy 3.1.1
- Flask-RESTful 0.3.10
- Flask-Marshmallow 0.15.0
- Flask-JWT-Extended 4.6.0
- PostgreSQL 15 (via Docker)
- pytest 7.4.0

> **Nota sobre versiones:** El spec original indica Flask 1.1.x, pero esta version es incompatible con Python 3.12+ debido a dependencias obsoletas en Jinja2, itsdangerous y Werkzeug. Se actualizo a Flask 2.3.3 con Werkzeug 2.3.8, que mantiene la misma API y comportamiento. Igualmente, psycopg2-binary se actualizo a 2.9.11 porque la version 2.9.6 no tiene wheels preconstruidos para Python 3.13 en Windows. En AWS Beanstalk (Python 3.9-3.11) estas versiones deberian funcionar sin problema segun la documentacion de AWS.

## Estructura del Proyecto

```
Entrega_1/
├── application.py                 # Entry point (Beanstalk busca la variable `application`)
├── docker-compose.yml             # PostgreSQL en Docker (puerto 5433)
├── requirements.txt               # Dependencias Python
├── Procfile                       # Comando de inicio para Beanstalk (gunicorn)
├── .env.example                   # Plantilla de variables de entorno
├── .gitignore
├── app/
│   ├── __init__.py                # App factory: create_app()
│   ├── config.py                  # Configuracion (prod y testing)
│   ├── models.py                  # Modelo BlacklistEntry (tabla blacklist_entries)
│   ├── schemas.py                 # Validacion de entrada con Marshmallow
│   ├── auth.py                    # Decorador @token_required (Bearer token estatico)
│   └── resources/
│       ├── blacklist.py           # POST /blacklists + GET /blacklists/<email>
│       └── health.py              # GET /health
├── tests/
│   ├── conftest.py                # Fixtures de pytest (app, client, auth_headers)
│   └── test_blacklist.py          # 4 tests: 2 positivos + 2 negativos
├── postman/
│   └── Blacklist_API.postman_collection.json  # Coleccion de Postman importable
└── .ebextensions/
    └── 01_flask.config            # Config WSGI para Beanstalk
```

## Prerequisitos

- **Python 3.13+** instalado
- **Docker Desktop** corriendo (para PostgreSQL)
- **Postman** (para pruebas de integracion)

## Como Levantar el Proyecto

### 1. Clonar el repositorio

```bash
git clone https://github.com/nicolasjaramillocely99/Devops_Miso.git
cd Devops_Miso
```

### 2. Levantar PostgreSQL con Docker

```bash
docker compose up -d
```

Esto levanta PostgreSQL en el **puerto 5433** (para no chocar con una instalacion local en 5432). Crea automaticamente la base de datos `blacklist_db`.

Crear la base de datos de testing manualmente:

```bash
PGPASSWORD=postgres psql -U postgres -h localhost -p 5433 -c "CREATE DATABASE blacklist_test_db;"
```

### 3. Crear entorno virtual e instalar dependencias

```bash
python -m venv venv
source venv/Scripts/activate    # Windows (Git Bash)
# source venv/bin/activate      # Linux/Mac
pip install -r requirements.txt
```


### 4. Arrancar la aplicacion

```bash
python application.py
```

La app estara disponible en `http://localhost:8000`.

## Endpoints del API

| Metodo | Ruta | Descripcion | Auth |
|--------|------|-------------|------|
| `GET` | `/health` | Health check del microservicio | No |
| `POST` | `/blacklists` | Agregar email a la lista negra | Bearer Token |
| `GET` | `/blacklists/<email>` | Consultar si un email esta en la lista negra | Bearer Token |

### POST /blacklists

**Headers:** `Authorization: Bearer <token>`, `Content-Type: application/json`

**Body:**
```json
{
    "email": "spam@example.com",
    "app_uuid": "550e8400-e29b-41d4-a716-446655440000",
    "blocked_reason": "Envio de spam recurrente"
}
```

- `email` (string, obligatorio): Email a agregar
- `app_uuid` (string, obligatorio): UUID de la aplicacion cliente
- `blocked_reason` (string, opcional, max 255 chars): Motivo del bloqueo

**Respuestas:** 201 (creado), 400 (datos invalidos), 401 (sin token)

### GET /blacklists/\<email\>

**Headers:** `Authorization: Bearer <token>`

**Respuesta:**
```json
{
    "is_blacklisted": true,
    "blocked_reason": "Envio de spam recurrente"
}
```

### GET /health

**Sin autenticacion.** Respuesta: `{"status": "healthy"}`

## Como Correr Tests Unitarios

Desde la raiz del proyecto, con el ambiente virtual activado:

```bash
pytest -v
```

Hay 3 tests (uno por endpoint) que usan mocks con `unittest.mock`, por lo que NO requieren PostgreSQL corriendo:
1. `test_health_endpoint_returns_ok` - GET /health
2. `test_post_blacklist_creates_entry` - POST /blacklists
3. `test_get_blacklist_returns_status` - GET /blacklists/<email>

## Como Usar Postman

### Importar la coleccion

1. Abrir Postman
2. Click en **Import**
3. Seleccionar el archivo `postman/Blacklist_API.postman_collection.json`

### Configurar variables

La coleccion trae variables predefinidas, pero si usas un **Environment** en Postman, asegurate de que tenga:

| Variable | Valor |
|----------|-------|
| `base_url` | `http://localhost:8000` |
| `token` | `default-dev-token` |

### Correr la coleccion

1. Click derecho en la coleccion > **Run**
2. Click en **Run Blacklist API - Entrega 1**
3. Todos los tests deben pasar (verde)

La coleccion incluye:
- Requests para los 3 endpoints con ejemplos de respuesta
- Carpeta "Casos negativos" (sin token, sin email, email no existente)
- Scripts de test (`pm.test`) que validan status codes y respuestas


