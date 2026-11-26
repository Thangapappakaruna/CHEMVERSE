from django.urls import path

from . import views

app_name = 'chemistry_dictionary'
urlpatterns = [
    path('', views.index, name='index'),
    path('api/search/', views.api_search, name='api_search'),
    path('<slug:slug>/', views.detail, name='detail'),
]
