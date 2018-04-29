
from blog.utils import find_modified_tags, datetimeformat, make_external,  calculate_work_date_stats, to_markdown



CODEVERSION = ':v0.7'

DATEFORMAT = '%A, %d %B %Y'


from . import BlogTestBase

class TestUtils(BlogTestBase):
    maxDiff = None

    def test_to_markdown(self):
        markdown_text = "body of post"
        self.assertEqual(markdown_text, to_markdown(markdown_text))