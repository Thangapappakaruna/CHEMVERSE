from django.urls import path

from . import views

app_name = 'reaction_builder'
urlpatterns = [
    path('', views.reaction_list, name='list'),
    path('new/', views.create, name='create'),
    path('api/check/', views.api_check, name='api_check'),
    path('<int:pk>/', views.detail, name='detail'),
    path('<int:pk>/edit/', views.create, name='edit'),
    path('<int:pk>/balance/', views.apply_balance, name='apply_balance'),
    path('<int:pk>/delete/', views.delete, name='delete'),
]
