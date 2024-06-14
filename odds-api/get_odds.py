import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()

def get_odds():
    API_KEY = os.getenv("API_KEY")
    SPORT_KEY = "soccer_usa_mls"
    params = {
        "apiKey": API_KEY,
        "regions": "us",
        "dateFormat": "unix"
    }
    url = f"https://api.the-odds-api.com/v4/sports/{SPORT_KEY}/odds/"
    odds = requests.get(url, params=params)
    return odds.json()


def get_scores():
    API_KEY = os.getenv("API_KEY")
    SPORT_KEY = "soccer_usa_mls"
    SPORT_KEY = "baseball_mlb"
    params = {
        "apiKey": API_KEY,
        "daysFrom": "1",
        "dateFormat": "unix"
    }
    url = f"https://api.the-odds-api.com/v4/sports/{SPORT_KEY}/scores/"
    scores = requests.get(url, params=params)
    return scores.json()



if __name__ == "__main__":
    scores = get_scores()
    now = datetime.now()
    now_str = now.strftime("%Y-%m-%d_%H_%M")

    with open(f"scores_{now_str}.json", "w", encoding="utf-8") as file:
        json.dump(scores, file)
    
