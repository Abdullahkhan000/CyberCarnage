import re
import requests
from datetime import date


def extract_steam_appid(url):
    match = re.search(r"/app/(\d+)", url)
    return int(match.group(1)) if match else None


RAWG_KEY = "63cf2eb2f87f495eacda5cb4bb5398fd"


def fetch_rawg_poster(game_name, slug=None):
    try:
        if slug:
            res = requests.get(f"https://api.rawg.io/api/games/{slug}?key={RAWG_KEY}")
            if res.status_code == 200 and res.json().get("background_image"):
                return res.json()["background_image"]

        res = requests.get(
            f"https://api.rawg.io/api/games?key={RAWG_KEY}&search={game_name}"
        )
        if res.status_code == 200 and res.json()["results"]:
            return res.json()["results"][0]["background_image"]

        return None
    except:
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
