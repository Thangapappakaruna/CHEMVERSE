from django.urls import path

from . import views

app_name = 'lab_simulator'
urlpatterns = [
    path('', views.index, name='index'),
    path('<slug:slug>/', views.experiment, name='experiment'),
    path('<slug:slug>/record/', views.record, name='record'),
]
