from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("tasks/", views.tasks, name="tasks"),
    path("tasks/new/", views.new_task, name="new_task"),
    path("tasks/<int:pk>/edit/", views.edit_task, name="edit_task"),
    path("tasks/<int:pk>/delete/", views.delete_task, name="delete_task"),
    path("tasks/<int:pk>/", views.task_details, name="task_details"),
]