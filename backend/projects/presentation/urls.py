from django.urls import path

from projects.presentation.views import ProjectGeneralView

urlpatterns = [
    path("", ProjectGeneralView.as_view(), name="project-general"),
]
