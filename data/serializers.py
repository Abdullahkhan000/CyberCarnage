from rest_framework import serializers
from .models import Games , GameInfo , About , ChatMessage , GuestUser
from .utils import extract_steam_appid, fetch_rawg_poster
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

class GameSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    game_name = serializers.CharField(
        max_length=200, help_text="Enter The Name Of The Game"
    )
    # company = serializers.CharField(help_text="Enter Company Names Of The Game")
    release_date = serializers.DateField()
    series = serializers.CharField(help_text="Enter Series Name Of The Game")
    developer = serializers.CharField()
    publisher = serializers.CharField()

    def create(self, validated_data):
        game = Games.objects.create(
            game_name=validated_data.get("game_name"),
            # company=validated_data.get("company"),
            release_date=validated_data.get("release_date"),
            series=validated_data.get("series"),
            developer=validated_data.get("developer"),
            publisher=validated_data.get("publisher"),

        )
        return game

    def update(self, instance, validated_data):
        instance.game_name = validated_data.get("game_name", instance.game_name)
        # instance.company = validated_data.get("company", instance.company)
        instance.release_date = validated_data.get(
            "release_date", instance.release_date
        )
        instance.series = validated_data.get("series", instance.series)
        instance.developer = validated_data.get("developer", instance.developer)
        instance.publisher = validated_data.get("publisher", instance.publisher)


        instance.save()
        return instance

class GameInfoSerializer(serializers.Serializer):
    game = serializers.IntegerField(write_only=True)
    multiplayer = serializers.BooleanField()
    playable = serializers.BooleanField()
    composer = serializers.CharField()

    def create(self, validated_data):
        game_id = validated_data.pop("game")
        game = Games.objects.get(id=game_id)

        return GameInfo.objects.create(
            game=game,
            **validated_data
        )

    def update(self, instance, validated_data):
        validated_data.pop("game", None)

        instance.multiplayer = validated_data.get("multiplayer", instance.multiplayer)
        instance.playable = validated_data.get("playable", instance.playable)
        instance.composer = validated_data.get("composer", instance.composer)

        instance.save()
        return instance


class AboutSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    # series from Games — read-only
    series = serializers.CharField(source='game.series', read_only=True)
    name = serializers.CharField(source='game.game_name', read_only=True)
    game = serializers.PrimaryKeyRelatedField(queryset=Games.objects.all())
    platform = serializers.CharField(max_length=200)
    steam_link = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    site_link = serializers.URLField(required=False, allow_blank=True)
    genre = serializers.CharField(max_length=200)
    steam_appid = serializers.IntegerField(required=False, allow_null=True)
    poster = serializers.CharField(required=False, allow_null=True)
    story = serializers.CharField(default="Story")

    def create(self, validated_data):
        game_obj = validated_data["game"]

        steam_link = validated_data.get("steam_link")
        steam_appid = extract_steam_appid(steam_link) if steam_link else None

        poster = fetch_rawg_poster(game_obj.game_name, getattr(game_obj, "slug", None))

        validated_data["steam_appid"] = steam_appid
        validated_data["poster"] = poster

        return About.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.platform = validated_data.get("platform", instance.platform)
        instance.steam_link = validated_data.get("steam_link", instance.steam_link)
        instance.site_link = validated_data.get("site_link", instance.site_link)
        instance.genre = validated_data.get("genre", instance.genre)
        instance.story = validated_data.get("story" ,instance.story)

        if "steam_link" in validated_data:
            instance.steam_appid = extract_steam_appid(instance.steam_link)

        if not instance.poster:
            instance.poster = fetch_rawg_poster(
                instance.game.game_name,
                getattr(instance.game, "slug", None)
            )

        instance.save()
        return instance


User = get_user_model()

class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(
        max_length=5000,
        allow_blank=False,
        trim_whitespace=True
    )

class ChatResponseSerializer(serializers.Serializer):
    response = serializers.CharField()
    remaining = serializers.IntegerField()

class GuestUserSerializer(serializers.Serializer):
    uuid = serializers.CharField(read_only=True)
    daily_count = serializers.IntegerField(read_only=True)
    last_used = serializers.DateField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    ip_address = serializers.IPAddressField(read_only=True)
    fingerprint = serializers.CharField(read_only=True)
    is_banned = serializers.BooleanField(read_only=True)

class ChatMessageSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    role = serializers.CharField(read_only=True)
    message = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

class ChatHistorySerializer(serializers.Serializer):
    messages = ChatMessageSerializer(many=True)