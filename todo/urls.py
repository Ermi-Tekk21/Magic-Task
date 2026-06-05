from django.urls import path
from . import views

urlpatterns = [
    path('', views.task_list),

    path('complete/<int:id>/', views.complete_task),
    path('toggle/<int:id>/', views.toggle_task),
    path('delete/<int:id>/', views.delete_task),
]