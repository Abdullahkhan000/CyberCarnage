from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
import uuid
from django.utils import timezone

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class Games(BaseModel):
    game_name = models.CharField(max_length=200)
    release_date = models.DateField()
    series = models.CharField(max_length=200)
    developer = models.CharField(max_length=200, default="Unknown Developer")
    publisher = models.CharField(max_length=200, default="Unknown Publisher")
    slug = models.SlugField(max_length=300, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.game_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.game_name} ({self.release_date})"


class About(BaseModel):
    game = models.ForeignKey(Games, on_delete=models.CASCADE, related_name="details")
    platform = models.CharField(max_length=200)
    steam_link = models.URLField(null=True, blank=True)
    site_link = models.URLField(default="", blank=True)
    genre = models.CharField(max_length=200)
    steam_appid = models.IntegerField(null=True, blank=True)
    poster = models.URLField(null=True, blank=True)
    story = models.TextField(default="Story not available")

    @property
    def series(self):
        return self.game.series

    def name(self):
        return self.game.game_name

    def __str__(self):
        return f"About {self.game.game_name}"


class GameInfo(BaseModel):
    game = models.OneToOneField(Games, on_delete=models.CASCADE, related_name="info")
    multiplayer = models.BooleanField(default=True)
    playable = models.BooleanField(default=True)
    composer = models.CharField(max_length=200, null=True, blank=True)

    @property
    def name(self):
        self.game.game_name

    def __str__(self):
        return f"Game Info for {self.game.game_name}"


class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    date_subscribed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class GuestUser(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    daily_count = models.IntegerField(default=0)
    last_used = models.DateField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    fingerprint = models.CharField(max_length=255, null=True, blank=True)
    is_banned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.uuid)

class ChatMessage(models.Model):
    ROLE_CHOICES = [("user", "User"), ("ai", "AI")]
    user = models.ForeignKey(GuestUser, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class GameRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey('Games', on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(default=0)  # 1-5 stars
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'game')