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
- **minIO** - S3 compatible file storage

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

A use case encapsulates a single application-level operation, such as creating or listing a project. It orchestrates the domain objects and depends on repository interfaces, applying the Dependency Inversion Principle (DIP) by interfaces. The use case should have its own dedicated command to ingest the payload from the outside world, keeping it decoupled from the web/API layer.

### Interfaces

Interfaces (ports) defined by the application layer describe capabilities such as persistence operations that the use cases depend on.

### Repository

The repository is the infrastructure implementation of the domain interfaces, mapping domain objects to Django ORM models.

### DRF View and serializers

The presentation layer exposes the API through DRF views and serializers, translating between HTTP requests/responses and the application layer's use cases and commands.

### 4. Handling constants and env variables

If you come across some arbitrary variable whos value influences logic in some way e.g. cache ttl, pagination size etc. Include it in the `settings.py` grouped under the comment telling from which django app it is derived and with a small comment on what it does

### 5. Returning data

API endpoints must always return data in JSON format. If some kind of error occurs, user must be informed about it via HTTP error code, and the JSON payload has property `details` with string description of error

## 6. File storage (MinIO / S3)

Files are not kept in the database – they are stored as objects in **MinIO**, an S3 compatible object storage that runs as the `s3` service from `docker-compose.yaml`. The backend talks to it through **boto3** (`backend/integrations/s3/client.py`).

Two terms worth knowing:

- **bucket** – a named container for objects, roughly a top level namespace (the app uses `projects` and `tasks`, see `S3_PROJECT_ATTACHMENT_BUCKET_NAME` and `S3_TASK_ATTACHMENT_BUCKET_NAME` in `settings.py`). Buckets are created by `make populate`.
- **object** – a single stored file, identified by a key (its full path inside the bucket) plus its content and metadata. Buckets are flat – there are no real directories, only keys that contain slashes, e.g. `attachments/2024/report.pdf`.

### Web GUI

MinIO ships with a browser based console for browsing buckets and uploading, downloading or deleting objects by hand:

- console: http://localhost:9001
- S3 API: http://localhost:9000

Log in with the `MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD` values from `.env`

## 7. Writing an endpoint

This section describes the end-to-end flow for adding a backend endpoint, using the project attachment delete flow as a reference (`ProjectAttachmentDetailView.delete`).

### 7.1. Layer responsibilities

An endpoint change usually touches all four layers:

| Layer          | Responsibility                                                               | Typical location        |
| -------------- | ---------------------------------------------------------------------------- | ----------------------- |
| Domain         | Business rules, entities, value objects, domain exceptions                   | `<app>/domain/`         |
| Application    | Use case orchestration, command/response DTOs, repository interfaces (ports) | `<app>/application/`    |
| Infrastructure | Django ORM models, repository implementations, external integrations         | `<app>/infrastructure/` |
| Presentation   | DRF views, serializers, URL routing, domain-to-HTTP exception mapping        | `<app>/presentation/`   |

Dependencies point inward: presentation depends on application/domain, application depends on domain and interfaces, infrastructure implements application interfaces.

### 7.2. Define or update domain behavior

Put business rules in domain entities or domain services, not in views.

- **Entities** (`domain/entities.py`) hold state and behavior. For example, `Project.delete_attachment()` validates that the project is not completed, finds the attachment, removes it from the aggregate, and returns it.
- **Domain exceptions** (`domain/exceptions.py`) extend `shared.domain.exceptions.DomainException` and represent business failures such as `ProjectNotFoundException`, `ProjectAttachmentNotFoundException`, or `ClosedProjectException`.

```py
class ProjectAttachmentNotFoundException(DomainException):
    """Raised when no project attachment was found."""

    def __init__(self):
        super().__init__("Specified project attachment was not found")
```

### 7.3. Define application interfaces

Declare repository ports in `application/interfaces.py`. Use cases depend on these abstractions, not on Django models.

- Inherit from `ABC` and use `RepositoryExceptionWrapper` as the metaclass.
- Declare methods as `@staticmethod @abstractmethod` when the repository is used as a static implementation.
- Include `_to_entity(...)` for mapping ORM models to domain entities.

```py
class ProjectAttachmentRepository(ABC, metaclass=RepositoryExceptionWrapper):
    @staticmethod
    @abstractmethod
    def delete(actor_id: UUID, project_id: UUID, attachment_id: UUID) -> int:
        """Delete attachment and return number of deleted rows."""
```

### 7.4. Implement the use case

Create one use case module per operation, e.g. `application/use_cases/delete_attachment.py`.

- **Command**: input DTO. Inherit from `shared.application.use_cases.base.Command`. Use `@dataclass(frozen=True, slots=True)`.
- **ResponseDTO**: output DTO. Inherit from `shared.application.use_cases.base.ResponseDTO`.
- **UseCase**: inherit from `shared.application.use_cases.base.UseCase` and implement `execute(command)`.

The use case should orchestrate domain objects and repositories. It should not depend on DRF request/response objects.

```py
@dataclass(frozen=True, slots=True)
class Command(BaseCommand):
    actor_id: UUID
    project_id: UUID
    attachment_id: UUID


@dataclass(frozen=True, slots=True)
class ResponseDTO(BaseResponseDTO):
    objects_deleted_count: int


class UseCase(BaseUseCase):
    def __init__(
        self,
        attachments: type[ProjectAttachmentRepository],
        projects: type[ProjectRepository],
    ) -> None:
        self._attachments = attachments
        self._projects = projects

    def execute(self, command: Command) -> ResponseDTO:
        project = self._projects.get(
            actor_id=command.actor_id, project_id=command.project_id
        )
        if project is None:
            raise ProjectNotFoundException()

        attachment_to_delete = project.delete_attachment(id=command.attachment_id)
        objects_deleted_count = self._attachments.delete(
            actor_id=command.actor_id,
            project_id=project.id,
            attachment_id=attachment_to_delete.id,
        )
        return ResponseDTO(objects_deleted_count=objects_deleted_count)
```

### 7.5. Implement infrastructure

Implement the repository interface in `infrastructure/repositories.py`.

- Query Django ORM models.
- Convert ORM models to domain entities through `_to_entity(...)`.
- Keep ORM details out of domain and application layers.
- Repository methods wrapped by `RepositoryExceptionWrapper` convert unexpected failures into `RepositoryException`.

```py
class DjangoProjectAttachmentRepository(ProjectAttachmentRepository):
    @staticmethod
    def delete(actor_id: UUID, project_id: UUID, attachment_id: UUID) -> int:
        return models.ProjectAttachment.objects.filter(
            id=attachment_id, project_id=project_id
        ).delete()[0]
```

When adding persistence fields, update `infrastructure/models.py` and create/apply Django migrations.

### 7.6. Add presentation layer

#### View

The DRF view translates HTTP to a command and delegates to the use case.

- Parse and validate input. Use DRF serializers for request bodies when the endpoint accepts payload data.
- Build a command from validated data and path/auth context.
- Instantiate the use case with concrete repositories.
- Execute the use case and return a `Response` with an explicit status code.

```py
class ProjectAttachmentDetailView(APIView):
    def delete(
        self,
        request: Request,
        project_id: UUID,
        attachment_id: UUID,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        command = delete_attachment.Command(
            actor_id=request.user.id,
            project_id=project_id,
            attachment_id=attachment_id,
        )
        use_case = delete_attachment.UseCase(
            projects=DjangoProjectRepository,
            attachments=DjangoProjectAttachmentRepository,
        )
        use_case.execute(command)
        return Response(status=status.HTTP_204_NO_CONTENT)
```

#### URL routing

Register the view in `<app>/presentation/urls.py` and make sure the app is included under `/api/` in `statusPulse/urls.py`.

```py
path(
    "<uuid:project_id>/attachments/<uuid:attachment_id>",
    view=views.ProjectAttachmentDetailView.as_view(),
    name="project-attachments-detail",
)
```

#### Exception mapping

Map domain exceptions to HTTP status codes in `<app>/presentation/exceptions.py`:

```py
EXCEPTION_MAPPER: Final[dict[BaseException, int]] = {
    domain_exceptions.ProjectNotFoundException: status.HTTP_404_NOT_FOUND,
    domain_exceptions.ProjectAttachmentNotFoundException: status.HTTP_404_NOT_FOUND,
}
```

Register the app mapper in `statusPulse/exceptions.py` by importing it and merging it into `ALL_EXCEPTION_MAPPER`. The custom DRF exception handler returns domain errors as:

```json
{
  "details": "Specified project attachment was not found"
}
```

For serializer validation errors handled directly in views, follow the existing project convention and return `details` (and `errors` when field-level details are needed).

### 7.7. Tests

Add tests at the layer where the behavior belongs:

- **Domain tests** (`<app>/tests/domain/`): entity rules and state transitions.
- **Application tests** (`<app>/tests/application/`): use case orchestration, usually with fake repositories/interfaces.
- **Presentation tests** (`<app>/tests/presentation/`): API contract, status codes, and response payloads.

Presentation tests should use realistic URLs via `reverse(...)`, assert HTTP status codes, and assert the error payload shape.

```py
url = reverse(
    "project-attachments-detail",
    kwargs={"project_id": project_id, "attachment_id": attachment_id},
)
response = self.client.delete(url)

self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
self.assertEqual(response.data.get("details"), "Specified project was not found")
```
