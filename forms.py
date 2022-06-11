from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length


class AddNewUserForm(FlaskForm):
    """Form for adding new users to application"""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(
        min=8, message='Password must be at least 8 characters long!')])
    image_url = StringField('Image URL (OPTIONAL)')


class EditUserForm(FlaskForm):
    """Form for updating a user profile"""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(
        min=8, message='Password must be at least 8 characters long!')])
    image_url = StringField('Image URL (OPTIONAL)')


class LoginForm(FlaskForm):
    """Form for logging a user in"""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class CommentForm(FlaskForm):
    """Small form for adding a new comment in the application."""

    comment = TextAreaField('Add New Comment', validators=[
                            DataRequired(message='Comments cannot be blank!')])

class EditCommentForm(FlaskForm):
    """form for editing current comment."""

    comment = TextAreaField('Update Comment', validators=[
                            DataRequired(message='Comments cannot be blank!')])