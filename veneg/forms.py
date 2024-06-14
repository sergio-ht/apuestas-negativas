from flask_wtf import FlaskForm
from wtforms import RadioField, SubmitField
from wtforms.fields.simple import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

from veneg.models import User



