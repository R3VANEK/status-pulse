from django.urls import path
from demo import views

urlpatterns = [
    path("programs", view=views.ProgramList.as_view()),
]
