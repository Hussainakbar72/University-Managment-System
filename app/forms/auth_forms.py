from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional, EqualTo

class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters long.')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match.')
    ])
    submit = SubmitField('Update Password')

class UserForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=64)])
    email = StringField('Email Address', validators=[DataRequired(), Email(), Length(max=120)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    password = PasswordField('Password (leave blank to keep unchanged)', validators=[Optional(), Length(min=6)])
    is_active = BooleanField('Is Active', default=True)
    role_id = SelectField('Primary Role', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save User')

class RoleForm(FlaskForm):
    name = StringField('Role Name', validators=[DataRequired(), Length(max=50)])
    description = StringField('Description', validators=[Optional(), Length(max=255)])
    submit = SubmitField('Save Role')

class UserRoleForm(FlaskForm):
    user_id = SelectField('User', coerce=int, validators=[DataRequired()])
    role_id = SelectField('Role', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Assign Role')
