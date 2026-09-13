from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Post, Comment, Profile

MAX_POST_IMAGE_SIZE = 5 * 1024 * 1024
MAX_AVATAR_SIZE = 2 * 1024 * 1024


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ["username", "email"]

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if not username:
            raise forms.ValidationError("Username is required.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        if password:
            validate_password(password, self.instance)
        return cleaned_data


class LoginForm(forms.Form):
    username = forms.CharField(label="Username")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["content", "image"]
        widgets = {
            "content": forms.Textarea(
                attrs={"rows": 3, "placeholder": "What's on your mind?", "maxlength": 500}
            ),
        }

    def clean_content(self):
        content = self.cleaned_data["content"].strip()
        if not content:
            raise forms.ValidationError("Post content cannot be empty.")
        return content

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image and image.size > MAX_POST_IMAGE_SIZE:
            raise forms.ValidationError("Post images must be 5 MB or smaller.")
        return image


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
        widgets = {"body": forms.TextInput(attrs={"placeholder": "Write a comment…", "maxlength": 300})}

    def clean_body(self):
        body = self.cleaned_data["body"].strip()
        if not body:
            raise forms.ValidationError("Comment cannot be empty.")
        return body


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["bio", "avatar"]
        widgets = {"bio": forms.Textarea(attrs={"rows": 3, "maxlength": 200})}

    def clean_bio(self):
        return self.cleaned_data["bio"].strip()

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")
        if avatar and avatar.size > MAX_AVATAR_SIZE:
            raise forms.ValidationError("Avatar images must be 2 MB or smaller.")
        return avatar
