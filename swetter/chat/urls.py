from django.urls import path , include
from . import views 
urlpatterns = [
    path('', views.chat_home, name='chat_home'),
     path('chat/<str:room_name>/', views.chat_room, name='chat'),
]