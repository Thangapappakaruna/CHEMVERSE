from django.urls import path

from . import views

app_name = 'chemistry_quiz'
urlpatterns = [
    path('', views.index, name='index'),
    path('play/', views.play, name='play'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('api/questions/', views.api_questions, name='api_questions'),
]
