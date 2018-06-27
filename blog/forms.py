from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField,\
    BooleanField, FieldList, FormField, Field, RadioField
from flask_wtf.file import FileField,  FileAllowed
from wtforms.validators import DataRequired
from flask_uploads import UploadSet, IMAGES


images_set = UploadSet('images', IMAGES)


class UploadForm(FlaskForm):
    images_field = FileField("images", validators=[FileAllowed(images_set, 'Images only!')])
    submit = SubmitField('Submit files')


class AnswerForm(FlaskForm):
    p_answer = StringField("", default="{{this.p_answer}}", _name="")
    is_correct = BooleanField(default="{{is_correct}}", _name="")



class AnswerRadioForm(FlaskForm):
    r_answers = RadioField("", choices= [])
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    title = StringField("", validators=[DataRequired()], default="{{title}}")
    body = TextAreaField("", default="{{body}}")
    summary = StringField("", default="{{summary}}")
    tags = StringField("", default="{{tags}}")
    category = StringField("", validators=[DataRequired()], default="{{category}}")
    answers = FieldList(FormField(AnswerForm), min_entries=4)
    submit = SubmitField('Save')

