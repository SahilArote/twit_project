from django.urls import path
from . import views
from .models import twit
from .views import search_user
from .views import api_users

urlpatterns = [
    path('', views.twit_list, name='twit_list'),
    path('create/', views.twit_create, name='twit_create'),
    path('<int:twit_id>/edit/', views.twit_edit, name='twit_edit'),
    path('<int:twit_id>/delete/', views.twit_delete, name='twit_delete'),
    path('register/', views.register, name='register'),
    path('search/', search_user, name='search_user'),
    path('api/users/', api_users, name='api_users' ),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path("profile/<str:username>/", views.user_profile, name="user_profile"),
    

]
