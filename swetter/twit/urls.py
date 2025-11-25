from django.urls import path
from . import views
from .models import twit
urlpatterns = [
    path('', views.twit_list, name='twit_list'),
    path('create/', views.twit_create, name='twit_create'),
    path('<int:twit_id>/edit/', views.twit_edit, name='twit_edit'),
    path('<int:twit_id>/delete/', views.twit_delete, name='twit_delete'),
    path('register/', views.register, name='register'),
    path('search/', views.search_user, name='search_user'),
  
    


    
]   