from django.urls import path

from . import views

app_name = 'boiling_melting'
urlpatterns = [
    path('', views.index, name='index'),
    path('compare/', views.compare, name='compare'),
    path('save/', views.save_comparison, name='save'),
    path('saved/<int:pk>/delete/', views.delete_comparison, name='delete'),
    path('api/data/', views.api_data, name='api_data'),
]
