import re
import requests

def extract_steam_appid(url):
    """
    Extract Steam AppID from: https://store.steampowered.com/app/570/Dota_2/
    """
    match = re.search(r'/app/(\d+)', url)
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