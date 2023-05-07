from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


app_name = "users"

urlpatterns = [
    path('', views.HomeView.as_view(), name='HomeView'),
    path('register/', views.RegisterView.as_view(), name='RegisterView'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='LoginView'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='LogoutView'),
    path('profile/', views.ProfileView.as_view(), name='ProfileView'),
    path('change_password/', views.ChangePasswordView.as_view(), name='ChangePasswordView'),
]
