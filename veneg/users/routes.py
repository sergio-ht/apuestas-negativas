import datetime
from flask import Blueprint, render_template, redirect, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from flask.helpers import url_for
from datetime import datetime
import argon2
from veneg import db, ph
from veneg.models import User, Match, Odd, Bet
from veneg.users.forms import LoginForm, RegistrationForm, PredictionForm


users = Blueprint("users", __name__)


@users.route("/")
def home():
    return render_template("home.html")



@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("users.home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        try:
            if user and ph.verify(user.password, form.password.data):
                # check if password needs rehash
                if ph.check_needs_rehash(user.password):
                    user.password = ph.hash(form.password.data)
                    db.session.commit()

                login_user(user, remember=form.remember.data)
                next_page = request.args.get("next")
                return redirect(next_page) if next_page else redirect(url_for("matches.next"))
        except argon2.exceptions.VerifyMismatchError:
            flash("Contraseña o correo incorrectos. Inténtalo nuevamente", "danger")
        else:
            flash("Contraseña o correo incorrectos. Inténtalo nuevamente", "danger")

    return render_template("login.html", title="Login", form=form)

@users.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("users.home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = ph.hash(form.password.data)
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_pw
        )
        db.session.add(user)
        db.session.commit()
        flash("Cuenta creada exitósamente", "success")
        return redirect(url_for("users.login"))
    return render_template("register.html", title="Crear Cuenta", form=form)

@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("users.home"))

@users.route("/prediction/<match_id>/update", methods=["GET", "POST"])
@login_required
def update_prediction(match_id):
    match = Match.query.get_or_404(match_id)
    if datetime.now() > match.date:
        flash("Can't bet on a match that has started or finished", "danger")
        return redirect(url_for("matches.next"))
    
    odds = Odd.query.filter_by(match_id=match.id)
    odds_dict = {}
    for odd in odds:
        if odd.team == match.home_team:
            odds_dict["home"] = odd
        elif odd.team == match.away_team:
            odds_dict["away"] = odd
        else:
            odds_dict["tie"] = odd

    form = PredictionForm()
    
    prediction = Bet.query.filter((Bet.match_id==match_id) & (Bet.user_id==current_user.id)).first()
    if not prediction:
        flash("No se pueden registrar apuestas en partidos ya empezados o finalizados", "info")
        return redirect(url_for("matches.match_info", match_id=match_id))
    

    if form.validate_on_submit():
        print("UPDATING BET....")
        odd_selection_id = odds_dict[form.prediction.data].id
        prediction.prediction = odd_selection_id
        db.session.commit()
        return redirect(url_for("matches.next"))

    
    for home_away, odd in odds_dict.items():
        if prediction.prediction == odd.id:
            form.prediction.data = home_away
            break

    return render_template("prediction.html", match=match, form=form, odds_dict=odds_dict)
    


@users.route("/account")
@login_required
def account():
    return render_template("account.html", title="Cuenta")


@users.route("/prediction/<match_id>", methods=["GET","POST"])
@login_required
def prediction(match_id):
    match = Match.query.get_or_404(match_id)
    if datetime.now() > match.date:
        flash("No se pueden registrar apuestas en partidos ya empezados o finalizados", "info")
        return redirect(url_for("matches.next"))
    bet = Bet.query.filter((Bet.match_id==match_id) & (Bet.user_id==current_user.id)).first()
    if bet:
        return redirect(url_for("users.update_prediction", match_id=match_id))
    
    odds = Odd.query.filter_by(match_id=match_id)
    odds_dict = {}
    for odd in odds:
        if odd.team == match.home_team:
            odds_dict["home"] = odd
        elif odd.team == match.away_team:
            odds_dict["away"] = odd
        else:
            odds_dict["tie"] = odd

    form = PredictionForm()
    if form.validate_on_submit():
        odd_selection_id = odds_dict[form.prediction.data].id
        bet = Bet(
            match_id=match_id,
            user_id=current_user.id,
            prediction=odd_selection_id
        )

        db.session.add(bet)
        db.session.commit()
        flash("Se reigstró correctamente la apuesta", "success")
        return redirect(url_for("matches.next"))

    return render_template("prediction.html", title="Predicción", match=match, form=form, odds_dict=odds_dict)

@users.route("/user/predictions/oncoming")
@login_required
def user_predictions_oncoming():
    page = request.args.get("page", 1, type=int)
    predictions = db.session.query(Bet).join(Match).filter((Match.result == None) & (Bet.user_id == current_user.id)).order_by(Match.date).paginate(page=page)
    
    return render_template("user_predictions_oncoming.html", predictions=predictions, title="Apuestas Siguientes")


@users.route("/user/predictions/past")
@login_required
def user_predictions_past():
    page = request.args.get("page", 1, type=int)
    predictions = db.session.query(Bet).join(Match).filter((Match.result != None) & (Bet.user_id == current_user.id)).order_by(Match.date.desc()).paginate(page=page)
    
    return render_template("user_predictions_past.html", predictions=predictions, title="Apuestas Finalizadas")


@users.route("/user/stats")
@login_required
def user_stats():
    total = Bet.query.filter_by(user_id=current_user.id).count()
    total = db.session.query(Bet).filter_by(user_id=current_user.id).count()
    correct = db.session.query(Bet.id, db.func.count(Bet.id), db.func.sum(Odd.value)).join(Odd).join(Match, Match.id==Odd.match_id).filter((Bet.user_id==current_user.id) & (Match.result==Bet.prediction)).first()
    wrong = db.session.query(Bet.id).join(Match, Match.id==Bet.match_id).filter((Bet.user_id==current_user.id) & (Match.result!=Bet.prediction)).count()

    # this month
    month_correct = db.session.query(Bet.id, db.func.sum(Bet.id), db.func.sum(Odd.value)).join(Odd).join(Match, Match.id == Bet.match_id)\
        .filter(Match.result == Bet.prediction)\
        .filter(Bet.user_id == current_user.id)\
        .filter(db.extract("year", Match.date) == datetime.now().year)\
        .filter(db.extract("month", Match.date) == datetime.now().month).first()
    month_wrong = db.session.query(Bet.id).join(Match, Match.id == Bet.match_id)\
        .filter(Match.result != None)\
        .filter(Match.result != Bet.prediction)\
        .filter(Bet.user_id == current_user.id)\
        .filter(db.extract("year", Match.date) == datetime.now().year)\
        .filter(db.extract("month", Match.date) == datetime.now().month).count()
    
    print(month_correct)
    print(month_wrong)
    return render_template("user_stats.html", total=total, correct=correct, wrong=wrong, month_correct=month_correct, month_wrong=month_wrong)


@users.route("/testing")
def testing():
    return render_template("layout2.html")