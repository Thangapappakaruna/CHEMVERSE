from django.urls import path

from . import views

app_name = 'community'
urlpatterns = [
    path('', views.post_list, name='list'),
    path('new/', views.create, name='create'),
    path('<int:pk>/', views.post_detail, name='detail'),
    path('<int:pk>/edit/', views.create, name='edit'),
    path('<int:pk>/like/', views.like, name='like'),
    path('<int:pk>/delete/', views.delete, name='delete'),
    path('reply/<int:pk>/delete/', views.delete_comment, name='delete_comment'),
]
