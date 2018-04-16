from blog.forms import PostForm

from google.appengine.ext import testbed
from . import BlogTestBase

from blog.models import BlogPost, Answer, Categories, Tags

class TestForms(BlogTestBase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, enable csrf for proper rendering of forms
        self.app.config['WTF_CSRF_ENABLED'] = True

    def test_post_form_names(self):
        form = PostForm()
        self.assertEqual(form.title.name, 'title')
        self.assertEqual(form.body.name, 'body')
        self.assertEqual(form.summary.name, 'summary')
        self.assertEqual(form.category.name, 'category')

       # self.assertEqual(form.answers[0].p_answer.value, 'p_answer')

    def test_hidden_form(self):
        form = PostForm()

        out = form.hidden_tag()
        assert(all(x in out for x in ('csrf_token')))

    def test_with_data(self):

        class DummyPostData(dict):
            def getlist(self, key):
                v = self[key]
                if not isinstance(v, (list, tuple)):
                    v = [v]
                return v


        postdict = DummyPostData({u'body': u'body text', u'category': u'category', u'updated': 'Monday, 16 April 2018',
                              u'tags': [u'a new tag', u'a new new tag'],
                                  u'timestamp': 'Monday, 16 April 2018', u'title': u'a title',
                                  u'answers': [{'is_correct': False, 'p_answer': u'a test answer'}],
                                  u'summary': u'this is a summary', u'id': '4'})


        form = PostForm(postdict)
        self.assertEqual(form.title.data, "a title")
        self.assertEqual(form.body.data, "body text")
        self.assertEqual(form.answers[0].p_answer.data, "a test answer")

