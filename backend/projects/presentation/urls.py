from django.urls import path
from projects.presentation import views

urlpatterns = [
    path(
        "<uuid:project_uuid>/attachments",
        view=views.ProjectAttachmentGeneralView.as_view(),
        name="project-attachments-general",
    ),
    path(
        "<uuid:project_uuid>/attachments/<uuid:attachment_uuid>",
        view=views.ProjectAttachmentDetailView.as_view(),
        name="project-attachments-detail",
    ),
]
