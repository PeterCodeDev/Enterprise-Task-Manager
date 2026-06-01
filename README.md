# Enterprise Task Manager

API REST de gestión de tareas con autenticación JWT, construida con **FastAPI + PostgreSQL + Docker**.

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Python 3.11, FastAPI, SQLAlchemy |
| Base de datos | PostgreSQL 15 |
| Autenticación | JWT + bcrypt |
| Migraciones | Alembic |
| Testing | pytest |
| Linting | Ruff |
| Frontend | Angular 17 + Nginx |
| Contenedores | Docker + Docker Compose |
| CI/CD | GitHub Actions |

## Requisitos

- Docker y Docker Compose
- Python 3.11+ (solo para desarrollo local)

## Instalación rápida

```bash
# 1. Clonar el repositorio
git clone https://github.com/PeterCodeDev/Enterprise-Task-Manager.git
cd Enterprise-Task-Manager

# 2. (Opcional) Personalizar variables de entorno
cp .env.example .env

# 3. Levantar todos los servicios
docker-compose up --build

# 4. Acceder
# Frontend: http://localhost
# API:      http://localhost:8000
# Swagger:  http://localhost:8000/docs
```

## Endpoints de la API

### Auth
| Método | Endpoint | Descripción | Auth |
|---|---|---|---|
| POST | `/api/auth/register` | Registro de usuario | No |
| POST | `/api/auth/login` | Login y obtener JWT | No |

### Tareas
| Método | Endpoint | Descripción | Auth |
|---|---|---|---|
| GET | `/api/tasks` | Listar tareas (paginado) | JWT |
| POST | `/api/tasks` | Crear tarea | JWT |
| GET | `/api/tasks/{id}` | Obtener tarea | JWT |
| PUT | `/api/tasks/{id}` | Actualizar tarea | JWT |
| PATCH | `/api/tasks/{id}/toggle` | Marcar/desmarcar completada | JWT |
| DELETE | `/api/tasks/{id}` | Eliminar tarea | JWT |

### Sistema
| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/health` | Health check |

### Parámetros de paginación (`GET /api/tasks`)
| Parámetro | Tipo | Default | Descripción |
|---|---|---|---|
| `page` | int | 1 | Número de página |
| `page_size` | int | 20 | Items por página (máx 100) |
| `completada` | bool | - | Filtrar por estado |

## Uso de la API

```bash
# 1. Registrar usuario
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"pass123"}'

# 2. Obtener token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"pass123"}'

# 3. Usar token para crear tarea
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"titulo":"Mi tarea","descripcion":"Descripción de la tarea"}'

# 4. Listar tareas con paginación
curl "http://localhost:8000/api/tasks?page=1&page_size=10&completada=false" \
  -H "Authorization: Bearer TU_TOKEN"
```

## Comandos útiles

```bash
# Ejecutar tests
docker-compose run --rm backend pytest tests/ -v

# Crear nueva migración
docker-compose run --rm backend alembic revision --autogenerate -m "descripcion"

# Aplicar migraciones
docker-compose run --rm backend alembic upgrade head

# Formatear código (Ruff)
pip install ruff
ruff check backend/ --fix
ruff format backend/

# Pre-commit hooks
pip install pre-commit
pre-commit install
```

## Estructura del proyecto

```
Enterprise-Task-Manager/
├── docker-compose.yml
├── .env.example
├── .pre-commit-config.yaml
├── .github/workflows/deploy.yml
├── backend/
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── requirements.txt
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   ├── app/
│   │   ├── main.py           ← Endpoints
│   │   ├── models.py         ← Modelos SQLAlchemy
│   │   ├── schemas.py        ← Validación Pydantic
│   │   ├── database.py       ← Conexión DB
│   │   ├── security.py       ← JWT + bcrypt
│   │   ├── auth.py           ← Dependencia auth
│   │   ├── exceptions.py     ← Manejo de errores
│   │   └── logging_config.py ← Logging estructurado
│   └── tests/
│       ├── conftest.py
│       └── test_tasks.py
└── frontend/
    └── ... (Angular 17 + Nginx)
```

## Variables de entorno

| Variable | Default | Descripción |
|---|---|---|
| `POSTGRES_USER` | taskuser | Usuario PostgreSQL |
| `POSTGRES_PASSWORD` | taskpass | Contraseña PostgreSQL |
| `POSTGRES_DB` | taskdb | Nombre BD |
| `DATABASE_URL` | postgresql://... | URL conexión BD |
| `SECRET_KEY` | dev-secret... | Clave firma JWT (cambiar en prod) |
| `LOG_LEVEL` | INFO | Nivel de logging |

## CI/CD

El workflow de GitHub Actions en cada push a `main`:
1. Ejecuta 22 tests
2. Construye imágenes Docker
3. Publica en GitHub Container Registry

## Licencia

MIT
