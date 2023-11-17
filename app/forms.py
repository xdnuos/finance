from flask_wtf import FlaskForm
from wtforms import (BooleanField, IntegerField, PasswordField, SelectField,
                     StringField, SubmitField)
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

from app.models import PaymentType, User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign In')
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
 
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')
 
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
class SpendingForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    amount = IntegerField('amount (x1000)', validators=[DataRequired()])
    type = StringField('type', validators=[DataRequired()])
    desc = StringField('description')
    # payment_type = SelectField('Payment Type')
    payment_type = SelectField('payment', choices=[(choice.value, choice.name) for choice in PaymentType], coerce=PaymentType, validators=[DataRequired()])