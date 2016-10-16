from google.appengine.api import search, memcache
from google.appengine.ext import db
import logging
from blog import app
from flask import request, jsonify
from datetime import datetime, timedelta, date


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



    
def create_document(doc_id,title, body, category, timestamp):
    return search.Document(doc_id=str(doc_id),
        fields=[search.TextField(name='title', value=title),
                search.TextField(name='body', value=body),
                search.TextField(name='category', value=category),
                search.DateField(name='date', value=timestamp)])
    



def createIndex(posts):

    try:
        if posts:
            for post in posts:
                doc_id=post.key()
                category=db.get(post.category.key()).category
                doc=create_document(doc_id,post.title,post.body, category, post.timestamp)
                search.Index(name=_INDEX_NAME).put(doc)
    except search.Error:
        logging.exception('Put failed')
        


