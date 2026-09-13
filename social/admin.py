from django.contrib import admin
from .models import Profile, Post, Comment, Like, Follow


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "bio"]


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["author", "content", "created_at"]
    list_filter = ["created_at"]


admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Follow)
