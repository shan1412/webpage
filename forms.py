from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from flask_login import LoginManager
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import DataRequired,Email,EqualTo
from wtforms import ValidationError



class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    Submit = SubmitField('Log in')



class RegistrationForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Email()])
    username = StringField('username',validators=[DataRequired()])
    password = PasswordField('password',validators=[DataRequired(),EqualTo('pass_confirm',message='password mismatch')])
    pass_confirm = PasswordField('Confirm password',validators=[DataRequired])
    submit = SubmitField('Register!')
    
    def check_email(self,field):
        if user.query.filter_by(email=field.data).first():
            raise ValidationError('Your email has been already registered!')
    
    def check_username(self,field):
        if user.query.filter_by(username=filed.data).first():
            raise ValidationError('Username already taken!')
         