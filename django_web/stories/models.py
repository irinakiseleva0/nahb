from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

#Link Flask story -> Django owner (Author).
#Used for Level 16 permissions: authors can edit/delete only their own stories.
class StoryOwnership(models.Model):
    story_id = models.IntegerField(unique=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_flask_stories",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"story {self.story_id} -> {self.owner}"

#Gameplay tracking.
class Play(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="plays",
    )
    story_id = models.IntegerField(db_index=True)
    ending_page_id = models.IntegerField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["story_id", "ending_page_id"]),
            models.Index(fields=["user", "story_id"]),
        ]

    def __str__(self):
        return f"Play(user={self.user_id}, story={self.story_id}, ending={self.ending_page_id})"

#Level 13: autosave progression (anonymous OR authenticated).
#For anonymous: use session_key (Django session id)
#For authenticated: also save user for convenience
class PlaySession(models.Model):
    session_key = models.CharField(max_length=64, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="play_sessions",
    )
    story_id = models.IntegerField(db_index=True)
    current_page_id = models.IntegerField()
    started_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["session_key", "story_id"],
                name="uniq_session_story_progress",
            )
        ]

    def __str__(self):
        return f"PlaySession(session={self.session_key}, story={self.story_id}, page={self.current_page_id})"

#Level 18: rating + comment (authenticated).
class Rating(models.Model):
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ratings",
    )
    story_id = models.IntegerField(db_index=True)
    stars = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "story_id"], name="uniq_user_story_rating")
        ]
        indexes = [
            models.Index(fields=["story_id"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"Rating(user={self.user_id}, story={self.story_id}, stars={self.stars})"

#Level 18: reports (authenticated) + moderation.
class Report(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reports",
    )
    story_id = models.IntegerField(db_index=True)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resolved_reports",
    )
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["story_id", "resolved"]),
        ]
        ordering = ["resolved", "-created_at"]

    def __str__(self):
        return f"Report(user={self.user_id}, story={self.story_id}, resolved={self.resolved})"
