from django.urls import path
from . import views
from .models import twit
from .views import search_user


urlpatterns = [
    path('', views.twit_list, name='twit_list'),
    path('create/', views.twit_create, name='twit_create'),
    path('<int:twit_id>/edit/', views.twit_edit, name='twit_edit'),
    path('<int:twit_id>/delete/', views.twit_delete, name='twit_delete'),
    path('register/', views.register, name='register'),
    path('search/', search_user, name='search_user'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path("profile/<str:username>/", views.user_profile, name="user_profile"),
    path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow_user'),
    path('profile/<str:username>/followers/', views.followers_list, name='followers_list'),
    path('profile/<str:username>/following/', views.following_list, name='following_list'),
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('comment/<int:post_id>/', views.comment_post, name='comment_post'),
    path('share/<int:post_id>/<int:recipient_id>/', views.share_post, name='share_post'),


    

]
