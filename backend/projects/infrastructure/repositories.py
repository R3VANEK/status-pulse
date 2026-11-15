from projects.application.interfaces import ProjectRepository
from projects.domain.entities import Project
from projects.domain.enums import ProjectStatus
from projects.infrastructure.models import Project as ProjectModel


class DjangoProjectRepository(ProjectRepository):
   pass
