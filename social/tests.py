from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from .models import Comment, Follow, Like, Post, Profile


def image_file(name="test.jpg", size=(50, 50), fmt="JPEG"):
    buffer = BytesIO()
    Image.new("RGB", size, "white").save(buffer, format=fmt)
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/jpeg")


class SocialPlatformTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("alice", "alice@example.com", "StrongPass123!")
        self.other = User.objects.create_user("bob", "bob@example.com", "StrongPass456!")
        self.post = Post.objects.create(author=self.other, content="Hello Pulse")

    def login(self, user=None):
        self.client.force_login(user or self.user)

    def test_profile_created_for_users(self):
        self.assertTrue(Profile.objects.filter(user=self.user).exists())

    def test_register_creates_hashed_password_and_profile(self):
        response = self.client.post(reverse("register"), {
            "username": "charlie",
            "email": "charlie@example.com",
            "password": "StrongPass789!",
            "confirm_password": "StrongPass789!",
        })
        self.assertRedirects(response, reverse("login"))
        charlie = User.objects.get(username="charlie")
        self.assertTrue(charlie.check_password("StrongPass789!"))
        self.assertTrue(Profile.objects.filter(user=charlie).exists())

    def test_registration_rejects_weak_password(self):
        response = self.client.post(reverse("register"), {
            "username": "charlie",
            "email": "charlie@example.com",
            "password": "password",
            "confirm_password": "password",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="charlie").exists())

    def test_registration_rejects_mismatched_passwords(self):
        response = self.client.post(reverse("register"), {
            "username": "charlie",
            "email": "charlie@example.com",
            "password": "StrongPass789!",
            "confirm_password": "DifferentPass789!",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="charlie").exists())

    def test_login_success(self):
        response = self.client.post(reverse("login"), {
            "username": "alice",
            "password": "StrongPass123!",
        })
        self.assertRedirects(response, reverse("feed"))

    def test_login_failure(self):
        response = self.client.post(reverse("login"), {
            "username": "alice",
            "password": "wrong-password",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_logout_requires_post(self):
        self.login()
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 405)

    def test_logout_post_works(self):
        self.login()
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("login"))

    def test_feed_requires_login(self):
        response = self.client.get(reverse("feed"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('feed')}")

    def test_feed_contains_own_and_followed_posts(self):
        self.login()
        own = Post.objects.create(author=self.user, content="My post")
        response = self.client.get(reverse("feed"))
        self.assertContains(response, own.content)
        self.assertNotContains(response, self.post.content)

        Follow.objects.create(follower=self.user, following=self.other)
        response = self.client.get(reverse("feed"))
        self.assertContains(response, self.post.content)

    def test_create_post(self):
        self.login()
        response = self.client.post(reverse("feed"), {"content": "A new post"})
        self.assertRedirects(response, reverse("feed"))
        self.assertTrue(Post.objects.filter(author=self.user, content="A new post").exists())

    def test_blank_post_is_rejected(self):
        self.login()
        response = self.client.post(reverse("feed"), {"content": "   "})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.filter(author=self.user).count(), 0)

    def test_post_image_size_limit(self):
        self.login()
        huge = SimpleUploadedFile(
            "huge.jpg", b"x" * (5 * 1024 * 1024 + 1), content_type="image/jpeg"
        )
        response = self.client.post(reverse("feed"), {"content": "image", "image": huge})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Post.objects.filter(author=self.user, content="image").exists())

    def test_post_delete_is_owner_only(self):
        self.login()
        response = self.client.post(reverse("post_delete", args=[self.post.id]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Post.objects.filter(id=self.post.id).exists())

    def test_post_delete_by_owner(self):
        self.login(self.other)
        response = self.client.post(reverse("post_delete", args=[self.post.id]))
        self.assertRedirects(response, reverse("feed"))
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())

    def test_like_toggle(self):
        self.login()
        url = reverse("post_like_toggle", args=[self.post.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["liked"])
        self.assertEqual(Like.objects.filter(post=self.post, user=self.user).count(), 1)

        response = self.client.post(url)
        self.assertFalse(response.json()["liked"])
        self.assertFalse(Like.objects.filter(post=self.post, user=self.user).exists())

    def test_like_requires_post(self):
        self.login()
        response = self.client.get(reverse("post_like_toggle", args=[self.post.id]))
        self.assertEqual(response.status_code, 405)

    def test_comment_creation(self):
        self.login()
        response = self.client.post(reverse("post_detail", args=[self.post.id]), {"body": "Nice!"})
        self.assertRedirects(response, reverse("post_detail", args=[self.post.id]))
        self.assertTrue(Comment.objects.filter(post=self.post, author=self.user, body="Nice!").exists())

    def test_blank_comment_rejected(self):
        self.login()
        response = self.client.post(reverse("post_detail", args=[self.post.id]), {"body": "   "})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Comment.objects.filter(post=self.post, author=self.user).exists())

    def test_follow_toggle(self):
        self.login()
        url = reverse("follow_toggle", args=[self.other.username])
        self.client.post(url)
        self.assertTrue(Follow.objects.filter(follower=self.user, following=self.other).exists())
        self.client.post(url)
        self.assertFalse(Follow.objects.filter(follower=self.user, following=self.other).exists())

    def test_self_follow_is_rejected(self):
        self.login()
        response = self.client.post(reverse("follow_toggle", args=[self.user.username]))
        self.assertRedirects(response, reverse("profile_detail", args=[self.user.username]))
        self.assertFalse(Follow.objects.filter(follower=self.user, following=self.user).exists())

    def test_profile_edit(self):
        self.login()
        response = self.client.post(reverse("profile_edit"), {
            "bio": "Developer",
        })
        self.assertRedirects(response, reverse("profile_detail", args=[self.user.username]))
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.bio, "Developer")

    def test_avatar_size_limit(self):
        self.login()
        huge = SimpleUploadedFile(
            "avatar.jpg", b"x" * (2 * 1024 * 1024 + 1), content_type="image/jpeg"
        )
        response = self.client.post(reverse("profile_edit"), {"bio": "", "avatar": huge})
        self.assertEqual(response.status_code, 200)
        self.user.profile.refresh_from_db()
        self.assertFalse(self.user.profile.avatar)

    def test_profile_pages_are_public(self):
        response = self.client.get(reverse("profile_detail", args=[self.other.username]))
        self.assertEqual(response.status_code, 200)

    def test_follow_lists_require_login(self):
        response = self.client.get(reverse("followers_list", args=[self.other.username]))
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('followers_list', args=[self.other.username])}",
        )
