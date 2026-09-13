from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),

    path("", views.feed, name="feed"),
    path("explore/", views.explore, name="explore"),

    path("post/<int:post_id>/", views.post_detail, name="post_detail"),
    path("post/<int:post_id>/delete/", views.post_delete, name="post_delete"),
    path("post/<int:post_id>/like/", views.post_like_toggle, name="post_like_toggle"),

    path("profile/edit/", views.profile_edit, name="profile_edit"),
    path("u/<str:username>/", views.profile_detail, name="profile_detail"),
    path("u/<str:username>/follow/", views.follow_toggle, name="follow_toggle"),
    path("u/<str:username>/followers/", views.followers_list, name="followers_list"),
    path("u/<str:username>/following/", views.following_list, name="following_list"),
]
