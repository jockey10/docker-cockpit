
from flask_wtf import Form
from wtforms.fields import *
from wtforms.validators import Required


class SignupForm(Form):
    name = TextField(u'Container Name', validators=[Required()])

    submit_kill = SubmitField(u'Kill!')
    submit_killrm = SubmitField(u'Kill and Remove!')
