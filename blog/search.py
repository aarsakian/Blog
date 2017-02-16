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

def delete_document(document_id):
    """deletes document from search index"""
    doc_index = search.Index(name=_INDEX_NAME)
    doc_index.delete(str(document_id))


def add_document_in_search_index(doc_id, title, body, summary, category, timestamp):
    document = create_document(doc_id, title, body, summary, category, timestamp)
    add_document_to_index(document)


def create_document(doc_id, title, body, summary, category, timestamp):
    return search.Document(doc_id=str(doc_id),
        fields=[search.TextField(name='title', value=title),
                search.TextField(name='body', value=body),
                search.TextField(name='summary', value=summary),
                search.TextField(name='category', value=category),
                search.DateField(name='date', value=timestamp)])
    

def add_document_to_index(document):
    try:
        index = search.Index(name=_INDEX_NAME)
        index.put(document)
    except search.Error:
        logging.exception('Search Indexing failed')


def query_search_index(query_string):
    try:
        query = search.Query(query_string=query_string, options=query_options)

        index = search.Index(name=_INDEX_NAME)
        return index.search(query)

        # process scored_document
    except search.Error:
        logging.error("Search Failed")
        raise search.Error


def delete_all_in_index():
    index = search.Index(name=_INDEX_NAME)
    # index.get_range by returns up to 100 documents at a time, so we must
    # loop until we've deleted all items.

        # Use ids_only to get the list of document IDs in the index without
        # the overhead of getting the entire document.
    document_ids = [logging.info("DOCS  "+document.doc_id) for document in index.get_range(ids_only=True)]

        # If no IDs were returned, we've deleted everything.


        # Delete the documents for the given IDs
  #  index.delete(document_ids)