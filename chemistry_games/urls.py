from django.urls import path

from . import views

app_name = 'chemistry_games'
urlpatterns = [
    path('', views.index, name='index'),
    path('api/submit/', views.submit, name='submit'),
    path('<slug:slug>/', views.play, name='play'),
]
