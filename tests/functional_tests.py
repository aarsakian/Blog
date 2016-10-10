import unittest
from selenium import webdriver


class NewVisitorTest(unittest.TestCase):  #

    def setUp(self):  #
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):  #
        self.browser.quit()

    def test_can_create_a_post_and_retrieve_it_later(self):  #
        #  after login I am directed to the main page
        self.browser.get('http://localhost:8000/edit')

        # I notice the page title and header mention my name and title of my blog
        self.assertIn('Armen Arsakian personal blog', self.browser.title)
        self.fail('Finish the test!')

        # The following fields must appear

        # A text field for the title

        # A text box for the body of the post

        # a text field for its category

        # a text field to write down a list of tags

        # There is a submit button to post the article

        # I hit submit button and the page updates again, showing my new article
        # as well the above fields available to submit a new post with a link
        # appearing in the title which directs to page dedicated to this new post.
        # Links appear for the tags and the category for which the post belongs to.




if __name__ == '__main__':  #
    unittest.main(warnings='ignore')  #



