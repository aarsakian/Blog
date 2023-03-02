from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField,\
    BooleanField, FieldList, FormField, Field, RadioField
from flask_wtf.file import FileField,  FileAllowed
from wtforms.validators import DataRequired
from flask_uploads import UploadSet, IMAGES


images_set = UploadSet('images', IMAGES)


class AnswerForm(FlaskForm):
    p_answer = StringField("", default="{{this.p_answer}}")
    is_correct = BooleanField(default="{{is_correct}}")


class AnswerRadioForm(FlaskForm):
    r_answers = RadioField("", choices= [])
    submit = SubmitField('Submit')


class ImageForm(FlaskForm):
    blob_key = StringField("", default="{{blob_key}}")
    filename = StringField("", default="{{filename}}")


class PostForm(FlaskForm):
    title = StringField("", validators=[DataRequired()], default="{{title}}")
    body = TextAreaField("", default="{{body}}")
    summary = StringField("", default="{{summary}}")
    tags = StringField("", default="{{#each tags}}{{this.val}},{{/each}}")
    category = StringField("", validators=[DataRequired()], default="{{category}}")
    answers = FieldList(FormField(AnswerForm), min_entries=4)
    images = FieldList(FormField(ImageForm), min_entries=0)
    images_upload = FileField("", validators=[FileAllowed(images_set, 'Images only!')])
    submit = SubmitField('Save')

