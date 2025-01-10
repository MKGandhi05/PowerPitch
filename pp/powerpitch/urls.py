from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.student_signup_view, name='signup'),
    path('faculty-signup/', views.faculty_signup_view, name='faculty_signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home, name='home'),

    path('profile/<str:user_id>/', views.profile_view, name='profile'),]