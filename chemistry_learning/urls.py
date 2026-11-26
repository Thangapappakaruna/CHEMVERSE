from django.urls import path

from . import views

app_name = 'chemistry_learning'
urlpatterns = [
    path('', views.lesson_list, name='list'),
    path('<slug:slug>/', views.lesson_detail, name='detail'),
    path('<slug:slug>/complete/', views.complete, name='complete'),
]
