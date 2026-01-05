import re
import requests
from datetime import date
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

def extract_steam_appid(url):
    match = re.search(r"/app/(\d+)", url)
    return int(match.group(1)) if match else None

def fetch_rawg_poster(game_name, slug=None):
    RAWG_KEY = settings.RAWG_API_KEY
    try:
        if slug:
            res = requests.get(
                f"https://api.rawg.io/api/games/{slug}?key={RAWG_KEY}",
                timeout=10
            )
            if res.status_code == 200 and res.json().get("background_image"):
                return res.json()["background_image"]

        res = requests.get(
            f"https://api.rawg.io/api/games?key={RAWG_KEY}&search={game_name}",
            timeout=10
        )
        if res.status_code == 200 and res.json().get("results"):
            return res.json()["results"][0]["background_image"]

    except Exception:
        return None

def can_use_ai(user, daily_limit=4):
    today = date.today()
    if user.last_used != today:
        user.daily_count = 0
        user.last_used = today
        user.save()

    return user.daily_count < daily_limit


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip

def get_obj_or_404(model, pk):
    if not pk:
        return None, Response({"error": "Primary key required"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        return model.objects.get(pk=pk), None
    except model.DoesNotExist:
        return None, Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)