from urllib.parse import urljoin
from datetime import date
from math import ceil
from mistune import markdown, HTMLRenderer
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from flask import g



from blog import app

from bleach import clean, linkify

allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img',
                  'table', 'th','tbody','tr','td','thead',
                'video', 'div', 'p', 'br', 'span', 'hr', 'src', 'class']

allowed_attrs = {'*': ['class'],
                        'a': ['href', 'rel'],
                        'img': ['src', 'alt']}


ALLOWED_EXTENSIONS = set([  'png', 'jpg', 'jpeg', 'gif'])



class BlogRenderer(HTMLRenderer):
    def table(self, header, body):
        """Rendering table element. Wrap header and body in it.
               :param header: header part of the table.
               :param body: body part of the table.
               """
        return (
                   '<table class="table table-bordered">\n<thead>%s</thead>\n'
                   '<tbody>\n%s</tbody>\n</table>\n'
               ) % (header, body)

    def table_cell(self, content, **flags):
        """Rendering a table cell. Like ``<th>`` ``<td>``.
        :param content: content of current table cell.
        :param header: whether this is header or not.
        :param align: align of current table cell.
        """
        if flags['header']:
            tag = 'th scope="col"'
        else:
            tag = 'td'
        align = flags['align']
        if not align:
            return '<%s>%s</%s>\n' % (tag, content, tag)
        return '<%s style="text-align:%s">%s</%s>\n' % (
            tag, align, content, tag
        )


def find_tags_to_be_removed(old_post_tags, non_modified_tags, remaining_tags):
    tags_candidate_to_be_removed = set(old_post_tags) - set(non_modified_tags)
    return find_modified_tags(tags_candidate_to_be_removed, remaining_tags)


def find_tags_to_be_added(editing_tags, non_modified_tags, remaining_tags):
    tags_candidate_to_be_added = set(editing_tags) - set(non_modified_tags)
    return find_modified_tags(tags_candidate_to_be_added, remaining_tags)


def find_modified_tags(candidate_tags, remaining_tags):
    if not isinstance(candidate_tags, set):
        candidate_tags = set(candidate_tags)  # loses order

    return candidate_tags - (candidate_tags & set(remaining_tags))


def datetimeformat(value, format='%A, %d %B %Y'):
    return value.strftime(format)

def to_markdown(text):
    renderer = BlogRenderer()
    return bleach_it(markdown(text,  escape=True, renderer=renderer))


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


def allowed_file(filename):
    return '.' in filename and \
           filename.lower().rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def confirm_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('current_user_uid') == g.current_user_uid:
            return True

        return False


