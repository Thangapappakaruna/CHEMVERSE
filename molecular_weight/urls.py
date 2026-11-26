from django.urls import path

from . import views

app_name = 'molecular_weight'
urlpatterns = [
    path('', views.index, name='index'),
    path('api/', views.api, name='api'),
]
