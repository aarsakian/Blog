
from blog.utils import find_modified_tags, datetimeformat, make_external,  calculate_work_date_stats, to_markdown
from google.appengine.ext import testbed




DATEFORMAT = '%A, %d %B %Y'


from . import BlogTestBase

class TestUtils(BlogTestBase):
    maxDiff = None

    def setUp(self):
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()

    def test_to_markdown(self):
        markdown_text = "body of post"
        self.assertEqual(u"<p>{}</p>\n".format(markdown_text), to_markdown(markdown_text))

    def test_for_xss_input(self):
        xss_input = 'an <script>evil()</script> example'

        self.assertNotEqual(u"{}".format(xss_input), to_markdown(xss_input))
        self.assertEqual(u"<p>an &lt;script&gt;evil()&lt;/script&gt; example</p>\n",
                         to_markdown(xss_input))

    def test_text_with_links_renders_to_html(self):
        text_with_link = "[I'm an inline-style link](https://www.google.com)"
        self.assertEqual('<p><a href="https://www.google.com" rel="nofollow">'
                         'I\'m an inline-style link</a></p>\n', to_markdown(text_with_link))

    def test_table_renders_to_html_with_classed(self):
        table = "| Header 1 | Header 2 |\n" \
                "| -------- | -------- |\n" \
                "| Cell 1 | Cell 2 |"

        rendered_table = u"<table class='table table-bordered'><thead><tr><th>Header 1</th><th>Header 2</th></tr>" \
                         u"</thead>" \
                         u"<tbody><tr><td>Cell 1</td><td>Cell 2</td></tr></tbody></table>"

        self.assertEqualHTML(rendered_table, to_markdown(table).strip())