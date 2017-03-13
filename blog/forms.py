from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    title = StringField("", validators=[DataRequired()], default="{{title}}")
    body = TextAreaField("", default="{{body}}")
    summary = StringField("", default="{{summary}}")
    tags = StringField("", default="{{tags}}")
    category = StringField("", validators=[DataRequired()], default="{{category}}")
    submit = SubmitField('Save')