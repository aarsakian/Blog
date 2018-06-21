from urlparse import urljoin
from datetime import datetime, date
from math import ceil
from markdown2 import markdown
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from uuid import UUID
from flask import g

from blog import app

from bleach import clean, linkify

allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img', 'video', 'div', 'p', 'br', 'span', 'hr', 'src', 'class']
allowed_attrs = {'*': ['class'],
                        'a': ['href', 'rel'],
                        'img': ['src', 'alt']}

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
    return bleach_it(markdown(text))


def bleach_it(text):
    return linkify(clean(text, tags=allowed_tags, strip=False, attributes=allowed_attrs))

def make_external(base_url, url):
    return urljoin(base_url, url)


def calculate_work_date_stats():
    passed_days = (date.today()-date(2012, 3, 2)).days
    remaining_days = int(ceil(2.0/3.0*8*365))-passed_days
    return passed_days, remaining_days


def generate_uid_token(expiration=3600):
    s = Serializer(app.config['SECRET_KEY'], expiration)
    return s.dumps({'current_user_uid': g.current_user_uid}).decode('utf-8')


def confirm_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('current_user_uid') == g.current_user_uid:
            return True

        return False