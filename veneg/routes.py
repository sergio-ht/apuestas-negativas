import argon2
from flask.helpers import url_for
import flask_sqlalchemy
# import requests
# from flask import jsonify, render_template, redirect, flash, request
# from flask_login import login_user, current_user, logout_user, login_required
# import os
# from dotenv import load_dotenv
# import json
# from datetime import datetime

# from sqlalchemy.util.langhelpers import counter


# from veneg import app, db, ph, login_manager
# from veneg.models import Match, Odd, Bet, User
# from veneg.forms import PredictionForm, LoginForm, RegistrationForm


# app.app_context().push()

# load_dotenv()


# def get_odds():
#     API_KEY = os.getenv("API_KEY")
#     # url = f"https://api.the-odds-api.com/v4/sports/?apiKey={API_KEY}"
#     SPORT_KEY = "soccer_usa_mls"
#     # url = f"https://api.the-odds-api.com/v4/sports/{SPORT_KEY}/odds/?apiKey={API_KEY}&regions=us&dateFormat=unix"
#     url = ""
#     odds = requests.get(url)
#     return odds.json()


# def read_odds(bookmaker, id):
#     odds = []
#     for outcome in bookmaker["markets"][0]["outcomes"]:
#         odd = Odd(
#             match_id=id,
#             team=outcome["name"],
#             value=outcome["price"]
#         )
#         odds.append(odd)
#     return odds


# def read_json_file():
#     # with open("veneg/data/odds_examples_short.json") as f:
#     with open("odds_2024-06-06_18_11.json") as f:
#         matches = json.load(f)
#     return matches









@app.route("/save-odds")
def save_odds():
    matches = read_json_file()
    for match in matches:
        new_match = Match(
            id=match.get("id"),
            home_team=match.get("home_team"),
            away_team=match.get("away_team"),
            date=datetime.fromtimestamp(match.get("commence_time"))
        )
        odds = read_odds(match.get("bookmakers")[0], new_match.id)
        for odd in odds:
            db.session.add(odd)
        db.session.add(new_match)
    db.session.commit()
    return matches


# USER




