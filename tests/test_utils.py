import pytest
from blog.utils import find_modified_tags, datetimeformat, make_external,  calculate_work_date_stats, to_markdown, \
    allowed_file

from tests import assertEqualHTML

DATEFORMAT = '%A, %d %B %Y'


def test_to_markdown():
    markdown_text = "body of post"
    u"<p>{}</p>\n".format(markdown_text) == to_markdown(markdown_text)


def test_for_xss_input():
    xss_input = 'an <script>evil()</script> example'

    assert "{}".format(xss_input) != to_markdown(xss_input)
    assert u"<p>an &lt;script&gt;evil()&lt;/script&gt; example</p>\n" ==\
                     to_markdown(xss_input)


def test_text_with_links_renders_to_html():
    text_with_link = "[I'm an inline-style link](https://www.google.com)"
    '<p><a href="https://www.google.com" rel="nofollow">' ==\
                     'I\'m an inline-style link</a></p>\n', to_markdown(text_with_link)


def test_table_renders_to_html_with_classed():
    table = "| Header 1 | Header 2 |\n" \
            "| -------- | -------- |\n" \
            "| Cell 1 | Cell 2 |"

    rendered_table = u"<table class='table table-bordered'><thead><tr><th>Header 1</th><th>Header 2</th></tr>" \
                     u"</thead>" \
                     u"<tbody><tr><td>Cell 1</td><td>Cell 2</td></tr></tbody></table>"
    with pytest.raises(Exception):
        assertEqualHTML(rendered_table, to_markdown(table).strip())


def test_allowed_extensions():
    not_allowed_file = 'test.txt'
    allowed_file_ext = 'myphoto.jpg'
    assert not allowed_file(not_allowed_file)
    assert allowed_file(allowed_file_ext)


def test_find_modified_tags():
    test_existing_tags = ["a new tag", "a new new tag"]
    editing_tags1 = ["a new tag 1", "a new new tag 2"]
    editing_tags2 = ["a new tag 1", "a new tag"]

    modified_tags = find_modified_tags(editing_tags1, test_existing_tags)
    assert modified_tags == editing_tags1

    modified_tags = find_modified_tags(editing_tags2, test_existing_tags)
    assert modified_tags == ["a new tag 1"]
