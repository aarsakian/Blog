import logging
from bs4 import BeautifulSoup as bs
import difflib
from blog.models import Tags, Posts, Categories, BlogPost, Answer

from flask_testing import TestCase


def assertEqualHTML(string1, string2, file1='', file2=''):
    """
    Compare two unicode strings containing HTML.
    A human friendly diff goes to logging.error() if there
    are not equal, and an exception gets raised.
    """

    def short(mystr):
        max = 20
        if len(mystr) > max:
            return mystr[:max]
        return mystr

    p = []
    for mystr, file in [(string1, file1), (string2, file2)]:
        if not isinstance(mystr, unicode):
            raise Exception(u'string ist not unicode: %r %s' % (short(mystr), file))
        soup = bs(mystr, 'html.parser')
        pretty = soup.prettify()
        p.append(pretty)
    if p[0] != p[1]:
        for line in difflib.unified_diff(p[0].splitlines(), p[1].splitlines(), fromfile=file1, tofile=file2):
            logging.error(line)
        raise Exception('Not equal %s %s' % (file1, file2))


class BlogTestBase(TestCase):
    maxDiff = None

    def create_app(self):
        from blog import app
        return app

    def tearDown(self):
        self.testbed.deactivate()

    def create_post(self, category="a category"):
        category_key = self.categories.add(category)

        test_tags = ["a new tag", "a new new tag"]
        tag_keys = self.tags.add(test_tags)

        summary = "a summmary"
        title = "a title"
        body = "here is a body"

        post_key = BlogPost(title=title,
                            body=body,
                            category=category_key,
                            tags=tag_keys,
                            summary=summary,
                            answers=()).put()

        return post_key.get(), category_key, tag_keys

    def assertEqualHTML(self, string1, string2, file1='', file2=''):
        """
        Compare two unicode strings containing HTML.
        A human friendly diff goes to logging.error() if there
        are not equal, and an exception gets raised.
        """

        def short(mystr):
            max = 20
            if len(mystr) > max:
                return mystr[:max]
            return mystr

        p = []
        for mystr, file in [(string1, file1), (string2, file2)]:
            if not isinstance(mystr, unicode):
                raise Exception(u'string ist not unicode: %r %s' % (short(mystr), file))
            soup = bs(mystr, 'html.parser')
            pretty = soup.prettify()
            p.append(pretty)
        if p[0] != p[1]:
            for line in difflib.unified_diff(p[0].splitlines(), p[1].splitlines(), fromfile=file1, tofile=file2):
                logging.error(line)
            raise Exception('Not equal %s %s' % (file1, file2))
