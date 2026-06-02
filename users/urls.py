from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('list/', views.user_list, name='user_list'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('skills/', views.skills_autocomplete, name='skills_autocomplete'),
    path('<int:pk>/', views.user_detail, name='user_detail'),
    path('<int:pk>/skills/add/', views.skill_add, name='skill_add'),
    path('<int:pk>/skills/<int:skill_id>/remove/', views.skill_remove, name='skill_remove'),
]
