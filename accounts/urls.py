from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = 'accounts'
urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.ChemLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('verify/<str:token>/', views.verify_email, name='verify_email'),
    path('verify-resend/', views.resend_verification, name='resend_verification'),
    path('profile/', views.my_profile, name='my_profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('u/<str:username>/', views.profile, name='profile'),
    path('history/', views.history, name='history'),
    path('saved/', views.saved, name='saved'),
    path('password/change/', views.ChangePasswordView.as_view(), name='password_change'),
    path('password/reset/', views.ResetView.as_view(), name='password_reset'),
    path('password/reset/sent/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('password/reset/<uidb64>/<token>/', views.ResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password/reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),
]
