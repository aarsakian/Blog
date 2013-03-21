from google.appengine.api import search, memcache
from google.appengine.ext import db
import logging
from blog import app
from flask import request, jsonify
from datetime import datetime, timedelta, date

televisions = {'name': 'hd televisions', 'children': []}
books = {'name': 'books', 'children': []}
KEY="posts"
ctree =  {'name': 'root', 'children': [books, televisions]}

# [The core fields that all products share are: product id, name, description,
# category, category name, and price]
# Define the non-'core' (differing) product fields for each category
# above, and their types.
product_dict =  {'hd televisions': {'size': search.NumberField,
                                 'brand': search.TextField,
                                 'tv_type': search.TextField},
                 'books': {'publisher': search.TextField,
                           'pages': search.NumberField,
                           'author': search.TextField,
                           'title': search.TextField,
                           'isbn': search.TextField}
                }

# sort results by author descending
expr_list = [search.SortExpression(
    expression='title', default_value='',
    direction=search.SortExpression.DESCENDING)]
# construct the sort options
sort_opts = search.SortOptions(
     expressions=expr_list)

query_options = search.QueryOptions(
    limit=10,
    sort_options=sort_opts)

_INDEX_NAME="posts"

def delete_document(document_ids):
    """deletes document from search index"""
    doc_index = search.Index(name=_INDEX_NAME)
    doc_index.remove(document_ids)



    
def create_document(doc_id,title, body,category):
    return search.Document(doc_id=str(doc_id),
        fields=[search.TextField(name='title', value=title),
                search.TextField(name='body', value=body),
                search.TextField(name='category', value=category),
                search.DateField(name='date', value=datetime.now().date())])
    



def createIndex(posts):

    try:
        if posts:
            for post in posts:
                doc_id=post.key()
                category=db.get(post.category.key()).category
                doc=create_document(doc_id,post.title,post.body,category)
                search.Index(name=_INDEX_NAME).put(doc)
    except search.Error:
        logging.exception('Put failed')
        


