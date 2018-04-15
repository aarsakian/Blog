from blog.forms import PostForm

from google.appengine.ext import testbed
from . import BlogTestBase

class TestForms(BlogTestBase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()

        self.form = PostForm()

    def test_post_form_names(self):

        self.assertEqual(self.form.title.name, 'title')
        self.assertEqual(self.form.body.name, 'body')
        self.assertEqual(self.form.summary.name, 'summary')
        self.assertEqual(self.form.category.name, 'category')

        #self.assertEqual(self.form.answers[0].p_answer.name, 'p_answer')

    def test_hidden_form(self):

        out = self.form.hidden_tag()
        assert(all(x in out for x in ('csrf_token')))

