from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import unittest

class NewVisitorTest(unittest.TestCase):  #

    def setUp(self):  #
        self.browser = webdriver.Chrome()

        self.browser.implicitly_wait(3)

    def tearDown(self):  #
        self.browser.quit()

    def can_login(self):

        self.browser.get('http://127.0.0.1:9082/login')

        admin_input_checkbox = self.browser.find_element_by_id('admin')

        admin_input_checkbox.click()

        self.browser.find_element_by_id("submit-login").click()

        # after I login i should see an edit link
        try:
            edit_element = WebDriverWait(self.browser, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "edit")))
        except:
            self.fail("did not locate the element")
        finally:
            self.assertEqual("Edit", edit_element.text)

    def test_can_create_a_post_and_retrieve_it_later(self):  #
        #  after login I am directed to the main page
        self.can_login()
        self.browser.get('http://127.0.0.1:9082/edit')

        # I notice the page title and header mention my name and title of my blog
        self.assertIn('Armen Arsakian personal blog', self.browser.title)
        # A text field for the title
        new_post_title_field = self.browser.find_element_by_id("new-post-title")
        # A text box for the body of the post
        new_post_body_textfield = self.browser.find_element_by_id("new-post-body")
        # a text field for its category
        new_post_category_field = self.browser.find_element_by_id("new-post-category")
        # a text field to write down a list of tags
        new_post_tags_field = self.browser.find_element_by_id("new-post-tags")

        summary_field = self.browser.find_element_by_id("new-post-summary")

        new_post_title_field.send_keys('my ultimate blog post')
        new_post_body_textfield.clear()

        new_post_body_textfield.send_keys('introducing TDD requires discipline which is not given')

        new_post_category_field.send_keys('cat1')

        new_post_tags_field.send_keys("tag1, tag2")

        summary_field.send_keys("a little summary")
        # There is a submit button to post the article
        self.browser.find_element_by_id("submit").click()
        post_key = ""

        try:
            wait = WebDriverWait(self.browser, 60)

            title_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".postTitle h3 a"))).text
            body_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".article"))).text

            tags = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "tag")))
            post_key = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data_element="data-id"]'))).text


        finally:

            self.assertEqual(u"my ultimate blog post", title_element)
            self.assertEqual(u"introducing TDD requires discipline which is not given", body_element)
            [self.assertIn(tag.text, "tag1, tag2") for tag in tags]
            self.assertNotEqual(post_key, "")


    # def test_can_view_all_posts_in_landing_page(self):
    #     #this is the landing page
    #     self.can_login()
    #     self.browser.implicitly_wait(1)
    #     self.browser.get('http://127.0.0.1:9082/')
    #
    # def test_can_add_a_tag_to_a_post(self):
    #     # an article has been submitted and I want to add a new tag
    #     # locate the tags
    #
    #     self.can_login()
    #     post_field_tags = self.browser.find_elements_by_class_name("tag")
    #     try:
    #         wait = WebDriverWait(self.browser, 90)
    #
    #         tags = []
    #
    #         for tag in post_field_tags:
    #             tags.append(tag.text)
    #             print len(post_field_tags), tag.text
    #         tags.append("tag3")
    #         self.browser.find_elements_by_class_name("edit-tags")[0].click()
    #     #    self.browser.execute_script("window.addEventListener('"
    #     #                            "load', function(){"
    #     #                            "document.getElementsByClassName('edit-tags')[0].click();}, false);");
    #
    #         print (",".join(tags))
    #
    #         self.browser.find_element_by_id("post_tag").send_keys(",".join(tags))
    #       #  after_saved_tags = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "tag")))
    #
    #     finally:
    #         pass
    #        # [self.assertIn(tag.text, tags) for tag in after_saved_tags]


if __name__ == '__main__':  #
     unittest.main(warnings='ignore')



