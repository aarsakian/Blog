from flask_wtf import Form
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import Required

class PostForm(Form):
    title = StringField('Add your title', validators=[Required()])
    body = TextAreaField('write your post')
    tags = StringField('Add your tags')
    category = StringField('category', validators=[Required()])
    submit = SubmitField('Submit')