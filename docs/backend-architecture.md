# Backend Architecture

## 1. Overview

The status-pulse backend uses **Django REST Framework (DRF)** to build and serve its REST API.

The stack in use:

- **Django** – web framework and ORM
- **Django REST Framework (DRF)** – API framework (views, serializers, request/response handling)
- **drf-spectacular** – OpenAPI schema generation, Swagger UI and ReDoc endpoints
- **PostgreSQL** – primary database
- **Redis + Celery** (`django-celery-beat`, `django-celery-results`) – asynchronous task queue and scheduled tasks
- **Flower** - easily monitor the celery tasks
- **uvicorn** – ASGI server for the Django application
- **gunicorn** – WSGI server (production entry point)
- **pytest + factory_boy** – testing stack

The API is mounted under the `/api/` prefix (see `statusPulse/urls.py`), with schema tooling exposed at:

- `/api/schema/` – OpenAPI schema (drf-spectacular)
- `/api/docs/` – Swagger UI
- `/api/redoc/` – ReDoc

## 2. Architecture

The backend project follows the DDD aproach with Clean Code Architecture principle

### 3. Folder structure

Each django app should have following file/folder structure. For this example we'll use the `orders` app:

```
backend/
│
├── statusPulse/
|   ├── settings.py
|   ├── urls.py
|   └── ...
|
├── orders/
│   ├── domain/
|   |   ├── entities.py
|   |   ├── value_objects.py
|   |   ├── enums.py
│   |   └── exceptions.py
|   |
|   ├── application/
|   |   ├── use_cases/
|   |   └── interfaces.py
|   |
|   ├── infrastructure/
|   |   ├── models.py
|   |   ├── repositories.py
|   |   └── migrations/
|   |
|   ├── presentiation/
|   |   ├── urls.py
|   |   ├── views.py
|   |   ├── permissions.py
|   |   └── serializers.py
|   |
|   ├── tests/
|   |   ├── domain/
|   |   ├── application/
|   |   └── presentation/
```

### Domain level

The domain layer contains the core business logic of the app: entities, value objects, enums and domain exceptions. It is independent of any framework concerns and should only import from python libraries or other domain level folders.

### Use case

A use case encapsulates a single application-level operation, such as creating or listing a program. It orchestrates the domain objects and depends on repository interfaces, applying the Dependency Inversion Principle (DIP) by interfaces. The use case should have its own dedicated command to ingest the payload from the outside world, keeping it decoupled from the web/API layer.

### Interfaces

Interfaces (ports) defined by the application layer describe capabilities such as persistence operations that the use cases depend on.

### Repository

The repository is the infrastructure implementation of the domain interfaces, mapping domain objects to Django ORM models.

### DRF View and serializers

The presentation layer exposes the API through DRF views and serializers, translating between HTTP requests/responses and the application layer's use cases and commands.

### 4. Handling constants and env variables

If you come across some arbitrary variable whos value influences logic in some way e.g. cache ttl, pagination size etc. Include it in the `settings.py` grouped under the comment telling from which django app it is derived and with a small comment on what it does
