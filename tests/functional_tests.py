
from selenium import webdriver
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException
import unittest, time


MAX_WAIT = 10

TITLE = 'my ultimate blog post'
SUMMARY = "a little summary"
BODY_TEXT = "introducing TDD requires discipline which is not given"

NEW_BODY_TEXT = u"TDD has sometimes synchronization issues"
NEW_TITLE = "a modified blog"
NEW_TAG = "tag3"
URL = 'http://127.0.0.1:8080/'


def make_orderer():
    order = {}

    def ordered(f):
        order[f.__name__] = len(order)
        return f

    def compare(a, b):
        return [1, -1][order[a] < order[b]]

    return ordered, compare

ordered, compare = make_orderer()
unittest.defaultTestLoader.sortTestMethodsUsing = compare


def wait(fn):
    def modified_fn(*args, **kwargs):
        start_time = time.time()
        while True:
            try:
                return fn(*args, **kwargs)
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)
    return modified_fn





class element_has_css_class(object):
  """An expectation for checking that an element has a particular css class.

  locator - used to find the element
  returns the WebElement once it has the particular css class
  """
  def __init__(self, locator, css_class):
    self.locator = locator
    self.css_class = css_class

  def __call__(self, driver):
    element = driver.find_element(*self.locator)   # Finding the referenced element
    if self.css_class in element.get_attribute("class"):
        return element
    else:
        return False


class NewVisitorTest(unittest.TestCase):  #

    def setUp(self):  #
        self.browser = webdriver.Chrome()

        self.browser.implicitly_wait(3)

    def tearDown(self):  #
        self.browser.quit()

    def wait_for_ajax(self, secs):
        wait = WebDriverWait(self.browser, secs)
        try:
            wait.until(lambda driver: driver.execute_script('return jQuery.active') == 0)
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        except Exception as e:
            pass

    def login_user(self):
        self.browser.get(URL + 'login')

        admin_input_checkbox = self.browser.find_element_by_id('admin')

        admin_input_checkbox.click()

        self.browser.find_element_by_id("submit-login").click()

    @ordered
    def test_can_login(self):
        print "testing login"
        self.login_user()
        # after I login i should see a submit button
        submit_button = self.browser.find_element_by_id("post-submit")
        self.assertTrue(submit_button)

    @ordered
    def test_create_a_post(self):
        print "creating a post"
        self.login_user()

        WebDriverWait(self.browser, 30).until(
                EC.presence_of_element_located((By.ID, 'new-post-title')))

        new_post_title_field = self.browser.find_element_by_id("new-post-title")
        # A text box for the body of the post
        new_post_body_textfield = self.browser.find_element_by_id("new-post-body")
        # a text field for its category
        new_post_category_field = self.browser.find_element_by_id("new-post-category")
        # a text field to write down a list of tags
        new_post_tags_field = self.browser.find_element_by_id("new-post-tags")

        summary_field = self.browser.find_element_by_id("new-post-summary")

        new_post_title_field.send_keys(TITLE)

        new_post_body_textfield.clear()
        new_post_body_textfield.send_keys(BODY_TEXT)

        new_post_category_field.send_keys('cat1')

        new_post_tags_field.send_keys("tag1, tag2")

        summary_field.send_keys(SUMMARY)
        # There is a submit button to post the article

        self.browser.find_element_by_id("post-submit").click()

        WebDriverWait(self.browser, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.postTitle h3')))
        title_el = self.browser.find_element_by_css_selector('.postTitle h3')
        self.assertEqual(title_el.text, TITLE)

    @ordered
    def test_edit_a_post(self):
        print "editing a post"
        self.login_user()

        self.browser.get(URL + 'articles/cat1/' + datetime.strftime(datetime.now(), '%B/%Y') +
                         '/my ultimate blog post')

        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-id]')))

        post_key = self.browser.find_element_by_css_selector("[data-id]").get_attribute('data-id')

        self.browser.get(URL + 'edit/' + post_key)

        summary_text = self.browser.find_element_by_id("new-post-summary").get_attribute("value")
        self.assertEqual(summary_text, SUMMARY)

        new_post_body_el = self.browser.find_element_by_id("new-post-body")
        self.assertEqual(new_post_body_el.get_attribute("value"), BODY_TEXT)
        new_post_body_el.clear()
        new_post_body_el.send_keys(NEW_BODY_TEXT)

        new_post_title_field = self.browser.find_element_by_id("new-post-title")
        new_post_title_field.clear()
        new_post_title_field.send_keys(NEW_TITLE)

        self.browser.find_element_by_id("post-submit").click()
        # self.wait_for_ajax(10)
        # WebDriverWait(self.browser, 30).until(
        #     EC.text_to_be_present_in_element((By.CSS_SELECTOR, '.post h3'), NEW_TITLE))
        # title_el = self.browser.find_element_by_css_selector('.post h3')
        # self.assertEqual(title_el.text, NEW_TITLE)

    @ordered
    def test_find_a_post(self):
        print "finding a post"
        self.browser.get(URL + 'articles/cat1/' + datetime.strftime(datetime.now(), '%B/%Y') + '/'
                         + NEW_TITLE)

        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '.page-header h1')))
        title_element = self.browser.find_element_by_css_selector(".page-header h1").text
        body_element = self.browser.find_element_by_css_selector(".article p").text

        tags = self.browser.find_elements_by_class_name("tags span")
        post_key = self.browser.find_element_by_css_selector("[data-id]").text

        self.assertEqual(NEW_BODY_TEXT, body_element)
        [self.assertIn(tag.text, u"tag1,tag2") for tag in tags]
        self.assertEqual(NEW_TITLE, title_element)
        self.assertNotEqual(post_key, "")

    def test_can_add_a_tag_to_a_post(self):
        # an article has been submitted and I want to add a new tag
        # locate the tags
        print "adding a tag to a post"
        self.login()

        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "edit-tags")))
        post_field_btn = self.browser.find_elements_by_class_name("edit-tags")
        post_field_btn.click()
        # try:
        #     wait = WebDriverWait(self.browser, 90)
        #
        #     tags = []
        #
        #     for tag in post_field_tags:
        #         tags.append(tag.text)
        #     tags.append(NEW_TAG)
        #     self.browser.find_elements_by_class_name("edit-tags")[0].click()
        #     #    self.browser.execute_script("window.addEventListener('"
        #     #                            "load', function(){"
        #     #                            "document.getElementsByClassName('edit-tags')[0].click();}, false);");
        #
        #     print (",".join(tags))
        #
        #     self.browser.find_element_by_id("post_tag").send_keys(",".join(tags))
        # #  after_saved_tags = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "tag")))
        #
        # finally:
        #     pass
        # [self.assertIn(tag.text, tags) for tag in after_saved_tags]

    @ordered
    def test_delete_a_post(self):
        print "deleting a post"
        self.login_user()

        self.browser.get(URL + 'edit')
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".destroy")))
        destroy_btn = self.browser.find_element_by_css_selector(".destroy")
        destroy_btn.click()
        try:
            WebDriverWait(self.browser, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".destroy")))
        except TimeoutException:
            pass
        self.browser.get(URL + 'Non existent URL')

        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '#bd h1')))
        content = self.browser.find_element_by_tag_name("details").text
       # print "C",content, self.browser.find_element_by_tag_name("details"), self.browser.title
     #   assert "404" in content





    # def test_can_view_all_posts_in_landing_page(self):
    #     #this is the landing page
    #     self.can_login()
    #     self.browser.implicitly_wait(1)
    #     self.browser.get('http://127.0.0.1:9082/')
    #



if __name__ == '__main__':
    unittest.main()