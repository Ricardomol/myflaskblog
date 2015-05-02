from flask.ext.wtf import Form
from flask.ext.babel import gettext
from flask.ext.pagedown.fields import PageDownField
from wtforms import StringField, BooleanField, TextAreaField
from wtforms.validators import Required, DataRequired, Length
from .models import User


class LoginForm(Form):
    username = StringField('username', validators=[DataRequired()])
    password = StringField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)


class EditForm(Form):
    nickname = StringField('nickname', validators=[DataRequired()])
    about_me = TextAreaField('about_me', validators=[Length(min=0, max=140)])

    def __init__(self, original_nickname, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.original_nickname = original_nickname

    def validate(self):
        if not Form.validate(self):
            return False
        if self.nickname.data == self.original_nickname:
            return True
        if self.nickname.data != User.make_valid_nickname(self.nickname.data):
            self.nickname.errors.append(gettext(
                'This nickname has invalid characters. '
                'Please use letters, numbers, dots and underscores only.'))
            return False
        user = User.query.filter_by(nickname=self.nickname.data).first()
        if user is not None:
            self.nickname.errors.append(gettext(
                'This nickname is already in use. '
                'Please choose another one.'))
            return False
        return True


class PostForm(Form):
    # post = StringField('post', validators=[DataRequired()])
    post = PageDownField("What have you learned?", validators=[Required()])


class SearchForm(Form):
    search = StringField('search', validators=[DataRequired()])

class ComposeForm(Form):

    title = StringField('title', validators=[DataRequired()])
    intro = StringField('intro', validators=[DataRequired()])
    body = TextAreaField('body', validators=[Length(min=0, max=6000)])
    # body_html = PageDownField("What have you learned?", validators=[Required()])
    # submit = SubmitField('Submit')