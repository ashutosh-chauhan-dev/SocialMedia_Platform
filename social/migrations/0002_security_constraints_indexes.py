from django.db import migrations, models
from django.db.models import F, Q


class Migration(migrations.Migration):

    dependencies = [
        ("social", "0001_initial"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="post",
            index=models.Index(fields=["author", "-created_at"], name="social_post_author_created_idx"),
        ),
        migrations.AddIndex(
            model_name="comment",
            index=models.Index(fields=["post", "created_at"], name="social_comment_post_created_idx"),
        ),
        migrations.AddConstraint(
            model_name="post",
            constraint=models.CheckConstraint(
                condition=~Q(content=""),
                name="post_content_not_empty",
            ),
        ),
        migrations.AddConstraint(
            model_name="comment",
            constraint=models.CheckConstraint(
                condition=~Q(body=""),
                name="comment_body_not_empty",
            ),
        ),
        migrations.AddIndex(
            model_name="like",
            index=models.Index(fields=["user", "post"], name="social_like_user_post_idx"),
        ),
        migrations.AddConstraint(
            model_name="follow",
            constraint=models.CheckConstraint(
                condition=~Q(follower=F("following")),
                name="cannot_follow_self",
            ),
        ),
        migrations.AddIndex(
            model_name="follow",
            index=models.Index(fields=["follower", "following"], name="social_follow_follower_following_idx"),
        ),
        migrations.AddIndex(
            model_name="follow",
            index=models.Index(fields=["following", "follower"], name="social_follow_following_follower_idx"),
        ),
    ]
