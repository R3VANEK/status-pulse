from django.urls import path
from projects.presentation import views

urlpatterns = [
    path(
        "<uuid:project_uuid>/attachments",
        view=views.ProjectAttachmentGeneralView.as_view(),
        name="project-attachments-general",
    ),
    path(
        "<uuid:project_id>/attachments/<uuid:attachment_id>",
        view=views.ProjectAttachmentDetailView.as_view(),
        name="project-attachments-detail",
    ),
]
