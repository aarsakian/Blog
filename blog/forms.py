from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, BooleanField, FieldList, FormField, Field
from wtforms.validators import DataRequired

import logging

class AnswerField(FlaskForm):
    p_answer = StringField("", default="{{p_answer}}", _name="")
    is_correct = BooleanField(default="{{is_correct}}", _name="")



class PostForm(FlaskForm):
    title = StringField("", validators=[DataRequired()], default="{{title}}")
    body = TextAreaField("", default="{{body}}")
    summary = StringField("", default="{{summary}}")
    tags = StringField("", default="{{tags}}")
    category = StringField("", validators=[DataRequired()], default="{{category}}")
    answers = FieldList(FormField(AnswerField), min_entries=1)
    submit = SubmitField('Save')

