from veneg import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    bets = db.relationship("Bet", backref="user", lazy=True)

    def __repr__(self) -> str:
        return f"User('{self.username}', '{self.email}')"

class Match(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    home_team = db.Column(db.String(100), nullable=False)
    away_team = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)    
    result = db.Column(db.Integer, db.ForeignKey("odd.id"), nullable=True, default=None)
    bets = db.relationship("Bet", backref="match", lazy=True)


    def __repr__(self) -> str:
        return f"Match({self.home_team} vs. {self.away_team})"


class Odd(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.String(50), db.ForeignKey("match.id"))
    team = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Float, nullable=False)

    def __repr__(self) -> str:
        return f"Odd({self.team}: {self.value})"

class Bet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.String(50), db.ForeignKey("match.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    prediction = db.Column(db.Integer, db.ForeignKey("odd.id"), nullable=False)
    value = db.Column(db.Float(), nullable=False, default=100.0)

    def __repr__(self) -> str:
        return f"Bet({self.match_id},{self.prediction})"

class BetBot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.String(50), db.ForeignKey("match.id"))
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    prediction = db.Column(db.Integer, db.ForeignKey("odd.id"), nullable=False)
    def __repr__(self) -> str:
        return f"BetBot({self.match_id},{self.prediction})"