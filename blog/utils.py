from urlparse import urljoin
from datetime import datetime, date
from math import ceil
from markdown2 import markdown

from bleach import clean, linkify

ALLOWED_TAGS  = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']



def find_tags_to_be_removed(old_post_tags, non_modified_tags, remaining_tags):
    tags_candidate_to_be_removed = set(old_post_tags) - set(non_modified_tags)
    return find_modified_tags(tags_candidate_to_be_removed, remaining_tags)


def find_tags_to_be_added(editing_tags, non_modified_tags, remaining_tags):
    tags_candidate_to_be_added = set(editing_tags) - set(non_modified_tags)
    return find_modified_tags(tags_candidate_to_be_added, remaining_tags)


def find_modified_tags(candidate_tags, remaining_tags):
    if not isinstance(candidate_tags, set):
        candidate_tags = set(candidate_tags)
        x = set(remaining_tags) & candidate_tags
    return list(candidate_tags - (set(remaining_tags) & candidate_tags))


def datetimeformat(value, format='%A, %d %B %Y'):
    return value.strftime(format)

def to_markdown(text):
    return linkify(clean(markdown(text)))


def make_external(base_url, url):
    return urljoin(base_url, url)


def calculate_work_date_stats():
    passed_days = (date.today()-date(2012, 3, 2)).days
    remaining_days = int(ceil(2.0/3.0*8*365))-passed_days
    return passed_days, remaining_days
