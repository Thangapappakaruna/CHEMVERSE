from django.urls import path

from . import views

app_name = 'molecular_structure'
urlpatterns = [
    path('', views.editor, name='editor'),
    path('gallery/', views.gallery, name='gallery'),
    path('save/', views.save, name='save'),
    path('<int:pk>/delete/', views.delete, name='delete'),
    path('api/<int:pk>/', views.api_structure, name='api_structure'),
]
