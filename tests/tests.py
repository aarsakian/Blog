import settings
import unittest
from flask import Flask
from flask_testing import TestCase


class MyTest(TestCase):

    def create_app(self):

        app = Flask(__name__)
        app.config.from_object('settings')
        app.config["DEBUG"] = True
        return app

    def test_edit_url_resolves_to_edit_page_view(self):
        print "SELF IS ", self.app
        response = self.client.get("/edit")#find the name of view
        self.assertEqual(response, home_page)

    def test_edit_page_returns_correct_html(self):
        request = HttpRequest() # create a request object
        response = home_page(request) # pass a view
            # insepct its contents
        self.assertTrue(response.content.startswith(b'<html>'))
        self.assertIn(b'<title>To-Do lists</title>', response.content)

        self.assertTrue(response.content.endswith(b'</html>'))


if __name__ == '__main__':
    unittest.main()