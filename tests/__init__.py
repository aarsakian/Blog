import logging

from google.appengine.ext import testbed
from blog import create_app as app_init
from flask_testing import TestCase



class BlogTestBase(TestCase):
    maxDiff = None

    def create_app(self):
        app = app_init('testing')
        return app

    def tearDown(self):
        self.testbed.deactivate()

    def assertEqualHTML(self, string1, string2, file1='', file2=''):
        """
        Compare two unicode strings containing HTML.
        A human friendly diff goes to logging.error() if there
        are not equal, and an exception gets raised.
        """

        from BeautifulSoup import BeautifulSoup as bs
        import difflib

        def short(mystr):
            max = 20
            if len(mystr) > max:
                return mystr[:max]
            return mystr

        p = []
        for mystr, file in [(string1, file1), (string2, file2)]:
            if not isinstance(mystr, unicode):
                raise Exception(u'string ist not unicode: %r %s' % (short(mystr), file))
            soup = bs(mystr)
            pretty = soup.prettify()
            p.append(pretty)
        if p[0] != p[1]:
            for line in difflib.unified_diff(p[0].splitlines(), p[1].splitlines(), fromfile=file1, tofile=file2):
                logging.error(line)
            raise Exception('Not equal %s %s' % (file1, file2))
