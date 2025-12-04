from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser

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

    def __str__(self):
        return f"Game Info for {self.game.game_name}"


class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    date_subscribed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
