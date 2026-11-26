from django.urls import path

from . import views

app_name = 'periodic_table'
urlpatterns = [
    path('', views.table, name='table'),
    path('api/elements/', views.api_elements, name='api_elements'),
    path('api/elements/<str:symbol>/', views.api_element, name='api_element'),
    path('<str:symbol>/', views.detail, name='detail'),
]
