from django.urls import path
from . import views

urlpatterns = [
    path('', views.task_list),
    path('signup/', views.signup, name='signup'),

    path('complete/<int:id>/', views.complete_task),
    path('toggle/<int:id>/', views.toggle_task),
    path('delete/<int:id>/', views.delete_task),

    path('ai-breakdown/', views.ai_breakdown, name='ai_breakdown'),
    path('smart-priority/', views.smart_priority, name='smart_priority'),
]
