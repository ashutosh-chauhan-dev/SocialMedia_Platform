from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import CommentForm, LoginForm, PostForm, ProfileForm, RegisterForm
from .models import Follow, Like, Post


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            messages.success(request, "Account created. Please log in.")
            return redirect("login")
    else:
        form = RegisterForm()
    return render(request, "social/register.html", {"form": form})


def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd["username"], password=cd["password"])
            if user is not None:
                login(request, user)
                return redirect("feed")
            messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, "social/login.html", {"form": form})


@require_POST
def user_logout(request):
    logout(request)
    return redirect("login")


@login_required
def feed(request):
    following_ids = request.user.following.values_list("following_id", flat=True)
    posts = (
        Post.objects.filter(Q(author_id__in=following_ids) | Q(author=request.user))
        .select_related("author", "author__profile")
    )

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, "Posted!")
            return redirect("feed")
    else:
        form = PostForm()

    suggestions = (
        User.objects.exclude(id=request.user.id)
        .exclude(id__in=following_ids)
        .order_by("?")[:5]
    )
    return render(request, "social/feed.html", {
        "posts": posts,
        "form": form,
        "suggestions": suggestions,
    })


@login_required
def explore(request):
    query = request.GET.get("q", "").strip()
    posts = Post.objects.select_related("author", "author__profile")
    if query:
        posts = posts.filter(Q(content__icontains=query) | Q(author__username__icontains=query))
    return render(request, "social/explore.html", {"posts": posts, "query": query})


@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post.objects.select_related("author", "author__profile"), id=post_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, "Comment added.")
            return redirect("post_detail", post_id=post.id)
    else:
        form = CommentForm()
    comments = post.comments.select_related("author", "author__profile")
    return render(request, "social/post_detail.html", {
        "post": post,
        "comments": comments,
        "form": form,
    })


@login_required
@require_POST
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    post.delete()
    messages.info(request, "Post deleted.")
    return redirect("feed")


@login_required
@require_POST
def post_like_toggle(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    return JsonResponse({"liked": liked, "likes_count": post.likes_count()})


def profile_detail(request, username):
    profile_user = get_object_or_404(User.objects.select_related("profile"), username=username)
    posts = profile_user.posts.select_related("author", "author__profile")
    is_following = (
        request.user.is_authenticated
        and request.user != profile_user
        and Follow.objects.filter(follower=request.user, following=profile_user).exists()
    )
    return render(request, "social/profile_detail.html", {
        "profile_user": profile_user,
        "posts": posts,
        "is_following": is_following,
    })


@login_required
@require_POST
def follow_toggle(request, username):
    target = get_object_or_404(User, username=username)
    if target == request.user:
        messages.error(request, "You can't follow yourself.")
        return redirect("profile_detail", username=username)

    follow, created = Follow.objects.get_or_create(follower=request.user, following=target)
    if not created:
        follow.delete()
        messages.info(request, f"Unfollowed {target.username}.")
    else:
        messages.success(request, f"Following {target.username}.")
    return redirect("profile_detail", username=username)


@login_required
def profile_edit(request):
    profile = request.user.profile
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("profile_detail", username=request.user.username)
    else:
        form = ProfileForm(instance=profile)
    return render(request, "social/profile_edit.html", {"form": form})


@login_required
def followers_list(request, username):
    profile_user = get_object_or_404(User, username=username)
    followers = User.objects.filter(following__following=profile_user).distinct()
    return render(request, "social/user_list.html", {
        "title": f"People following {profile_user.username}",
        "users": followers,
    })


@login_required
def following_list(request, username):
    profile_user = get_object_or_404(User, username=username)
    following = User.objects.filter(followers__follower=profile_user).distinct()
    return render(request, "social/user_list.html", {
        "title": f"People {profile_user.username} follows",
        "users": following,
    })
