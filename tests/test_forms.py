from blog.forms import PostForm,  AnswerRadioForm

from google.appengine.ext import testbed
from . import BlogTestBase

from blog.models import BlogPost, Answer, Categories, Tags

TEST_IMAGE = u'2019_1_4_16z.gif'


class TestForms(BlogTestBase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, enable csrf for proper rendering of forms
        self.app.config['WTF_CSRF_ENABLED'] = True
        self.testbed.init_blobstore_stub()
        self.testbed.init_datastore_v3_stub()

        self.testbed.init_app_identity_stub()

        self.testbed.init_urlfetch_stub()

        # enable memcache
        self.testbed.init_memcache_stub()
        self.categories = Categories()
        self.tags = Tags()

    def test_post_form_names(self):
        form = PostForm()
        self.assertEqual(form.title.name, 'title')
        self.assertEqual(form.body.name, 'body')
        self.assertEqual(form.summary.name, 'summary')
        self.assertEqual(form.category.name, 'category')
        self.assertEqual(form.images.name, 'images')

    def test_hidden_form(self):
        form = PostForm()

        out = form.hidden_tag()
        answer_form = AnswerRadioForm()
        answer_out = answer_form.hidden_tag()
        assert(all(x in out for x in ('csrf_token')))
        assert (all(x in answer_out for x in ('csrf_token')))

    def test_with_data_using_obj(self):

        category_key = self.categories.add("category")

        test_tags = ["a new tag", "a new new tag"]
        new_tag_keys = self.tags.add(test_tags)

        answer = Answer(p_answer="a test answer",
               is_correct=False)

        with open(TEST_IMAGE, 'rb') as f:
                byte_content = f.read()

        post = BlogPost(title="a title", body= "body text", category=category_key, tags=new_tag_keys,
                        summary="this is a summary", answers=[answer])

        post.add_blob(byte_content, TEST_IMAGE)

        post.put()
        form = PostForm(obj = post)

        self.assertEqual(form.title.data, "a title")
        self.assertEqual(form.body.data, "body text")
        self.assertEqual(form.answers[0].p_answer.data, "a test answer")
        self.assertEqual(form.images[0].filename.data, TEST_IMAGE)


    def test_with_data_using_dict(self):

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

        form.answers.append_entry([{'is_correct': False, 'p_answer': u'a test answer'}])
        self.assertEqual(form.title.data, "a title")
        self.assertEqual(form.body.data, "body text")
       # self.assertEqual(form.answers[0].p_answer.data, "a test answer")

    def test_answers_radio_form(self):

        answers = [("a correct answer",""), ("a wrong answer","")]
        form = AnswerRadioForm()
        form.r_answers.data = "a test answer"
        self.assertEqual(form.r_answers.data, "a test answer")


    def tearDown(self):
        self.app.config['WTF_CSRF_ENABLED'] = False
