from django.urls import path

from . import views

app_name = 'compound_search'
urlpatterns = [
    path('', views.search, name='search'),
    path('add/', views.add, name='add'),
    path('api/search/', views.api_search, name='api_search'),
    path('<int:pk>/', views.detail, name='detail'),
    path('<int:pk>/favorite/', views.toggle_favorite, name='favorite'),
]
