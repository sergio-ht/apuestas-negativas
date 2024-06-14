from flask import Blueprint, render_template, request
from flask_login import login_required
from datetime import datetime
# from veneg import db, app
from veneg import db
from veneg.models import BetBot, Match, Odd, Bet

bots = Blueprint("bots", __name__)

# current_app.app_context().push()

@bots.route("/bot")
@login_required
def next():
    betbots = db.session.query(BetBot.prediction, Match.id, Match.home_team, Match.away_team, Match.date, Odd.team)\
        .join(Match, BetBot.match_id==Match.id)\
        .join(Odd, BetBot.prediction==Odd.id)\
        .filter(
            Match.date > datetime.now()
        ).all()
    print(betbots)

    return render_template("bot.html", predictions=betbots)
    page = request.args.get("page", 1, type=int)
    matches = db.session.query(Match).filter(Match.date > datetime.now()).filter(~ db.exists().where((Match.id==Bet.match_id) & (Bet.user_id==current_user.id))).paginate(per_page=10, page=page)
    return render_template("next_matches.html", title="Siguientes Partidos", matches=matches)

@bots.route("/match/<match_id>")
def match_info(match_id):
    match = Match.query.get_or_404(match_id)
    bets = db.session.query(Bet.prediction, Odd.team, db.func.count(Bet.prediction)).join(Odd).filter(Bet.match_id == match_id).group_by(Bet.prediction).all()
    labels = [bet[1] for bet in bets]
    values = [bet[2] for bet in bets]
    now = datetime.now()
    # odds = Odd.query.filter_by(match_id=match.id).all()
    # freq = {}
    # for odd in odds:
    #     freq[odd.team] = Bet.query.filter_by(prediction=odd.id).count()
    # labels = list(freq.keys())
    # values = list(freq.values())
    return render_template("match.html", title=f"{match.home_team} vs {match.away_team}",match=match, now=now, labels=labels, values=values)
