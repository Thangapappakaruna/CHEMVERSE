from django.urls import path

from . import views

app_name = 'reaction_balancer'
urlpatterns = [
    path('', views.index, name='index'),
    path('api/', views.api_balance, name='api'),
]
