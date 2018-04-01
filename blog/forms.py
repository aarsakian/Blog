from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, RadioField, FieldList, FormField
from wtforms.validators import DataRequired

import logging

class AnswersField(RadioField):
    def _value(self):
        if self.data:
            logging.info("VAAL {}".format(self.data))
            return u', '.join(self.data)
        else:

            return u''


class IMForm(FlaskForm):
    protocol = RadioField(choices=[('aim', 'AIM'), ('msn', 'MSN')], default="{{radio_field}}")




class PostForm(FlaskForm):
    title = StringField("", validators=[DataRequired()], default="{{title}}")
    body = TextAreaField("", default="{{body}}")
    summary = StringField("", default="{{summary}}")
    tags = StringField("", default="{{tags}}")
    category = StringField("", validators=[DataRequired()], default="{{category}}")
    radio_field = FieldList(FormField(IMForm))
    submit = SubmitField('Save')

