from django.conf import settings
from django.db import models

from django.contrib.auth.models import User


class StoryLink(models.Model):
    flask_story_id = models.IntegerField(unique=True)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owned_stories")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Story {self.flask_story_id} -> {self.owner.username}"


class Play(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, blank=True,
    )
    story_id = models.IntegerField()
    ending_page_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Play(story={self.story_id}, ending={self.ending_page_id})"


class StoryOwnership(models.Model):
    story_id = models.IntegerField(unique=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"story {self.story_id} -> {self.owner}"


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    story_id = models.IntegerField()
    stars = models.IntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "story_id")


class Report(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    story_id = models.IntegerField()
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
