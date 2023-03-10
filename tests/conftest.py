import uuid
import pytest
import os
import itertools
from google.cloud import datastore
from google.cloud import ndb, storage
from unittest import mock
import requests
import urllib3
from six.moves import http_client
from google.api_core.client_options import ClientOptions
import json
from blog.models import Answer, BlogPost, Tags, Categories, Posts

KIND = "SomeKind"
OTHER_KIND = "OtherKind"
OTHER_NAMESPACE = "other-namespace"



EXTERNAL_URL = os.getenv("EXTERNAL_URL", "https://127.0.0.1:4443")
PUBLIC_HOST = os.getenv("PUBLIC_HOST", "storage.gcs.127.0.0.1.nip.io:4443")

storage.blob._API_ACCESS_ENDPOINT = "https://" + PUBLIC_HOST
storage.blob._DOWNLOAD_URL_TEMPLATE = (
    u"%s/download/storage/v1{path}?alt=media" % EXTERNAL_URL
)
storage.blob._BASE_UPLOAD_TEMPLATE = (
    u"%s/upload/storage/v1{bucket_path}/o?uploadType=" % EXTERNAL_URL
)
storage.blob._MULTIPART_URL_TEMPLATE = storage.blob._BASE_UPLOAD_TEMPLATE + u"multipart"
storage.blob._RESUMABLE_URL_TEMPLATE = storage.blob._BASE_UPLOAD_TEMPLATE + u"resumable"




def all_entities(client):
    return itertools.chain(
        client.query(kind=KIND).fetch(),
        client.query(kind=OTHER_KIND).fetch(),
        client.query(namespace=OTHER_NAMESPACE).fetch(),
    )



def _make_ds_client(namespace, g_credentials):

    emulator = bool(os.environ.get("DATASTORE_EMULATOR_HOST"))
    if emulator:
        client = datastore.Client(project="test", credentials=g_credentials,
                                  namespace=namespace, _http=requests.Session)
    else:
        client = datastore.Client(namespace=namespace)

    return client




@pytest.fixture
def namespace():
    return str(uuid.uuid4())




@pytest.fixture
def to_delete():
    return []


@pytest.fixture
def tags(client_context):
    return Tags()


@pytest.fixture
def categories(client_context):
    return Categories()


@pytest.fixture
def posts(client_context):
    return Posts()


@pytest.fixture(scope="session")
def deleted_keys():
    return set()


@pytest.fixture(scope="module", autouse=True)
def initial_clean():
    # Make sure database is in clean state at beginning of test run
    import google.auth.credentials
    return mock.Mock(spec=google.auth.credentials.Credentials)
    client = datastore.Client(credentials=credentials)
    for entity in all_entities(client):
        client.delete(entity.key)


@pytest.fixture
def dispose_of(with_ds_client, to_delete):
    def delete_entity(ds_keys):
        to_delete.extend([ds_key._key for ds_key in ds_keys])
    return delete_entity


@pytest.fixture
def g_credentials():
    import google.auth.credentials
    return mock.Mock(spec=google.auth.credentials.Credentials)


@pytest.fixture
def with_ds_client(ds_client, to_delete, deleted_keys):
    # Make sure we're leaving database as clean as we found it after each test
    results = [
        entity
        for entity in all_entities(ds_client)
        if entity.key not in deleted_keys
    ]
    assert not results

    yield ds_client

    if to_delete:
        ds_client.delete_multi(to_delete)
        deleted_keys.update(to_delete)

    not_deleted = [
        entity
        for entity in all_entities(ds_client)
        if entity.key not in deleted_keys
    ]
    assert not not_deleted


@pytest.fixture
def ds_client(namespace, g_credentials):
    return _make_ds_client(namespace, g_credentials)




@pytest.fixture(autouse=True)
def client_context(namespace, g_credentials):

    client = ndb.Client(project="test", namespace=namespace, credentials=g_credentials)
    with client.context(cache_policy=False, legacy_data=False) as the_context:
        yield the_context


@pytest.fixture
def test_bucket(storage_client):
    return storage_client.create_bucket('test-bucket')


@pytest.fixture
def storage_client(namespace, g_credentials):
    my_http = requests.Session()
    my_http.verify = False  # disable SSL validation
    urllib3.disable_warnings(
        urllib3.exceptions.InsecureRequestWarning
    ) # disable https warnings for https insecure certs

    client = storage.Client(project="test", credentials=g_credentials,
                               _http=my_http,
                               client_options=ClientOptions(api_endpoint=EXTERNAL_URL))

    yield client
    for bucket in client.list_buckets():
        # List the Blobs in each Bucket
        #print ("cleaning", bucket.list_blobs()[0])
        blobs = list(bucket.list_blobs())
        bucket.delete_blobs(blobs, on_error=lambda blob: None)




@pytest.fixture
def post_with_answers(client_context, tags, categories, answer_keys, dispose_of):

    category = "a category"
    test_tags = ["a new tag", "a new new tag"]
    tag_keys = tags.add(test_tags)

    category_key = categories.add(category)
    summary = "a summmary"
    title = "a title"
    body = "here is a body"
    answers = [answer_key.get() for answer_key in answer_keys]
    post_key = BlogPost(title=title,
                        body=body,
                        category=category_key,
                        tags=tag_keys,
                        summary=summary,
                        answers=answers).put()

    yield post_key.get(), category_key, tag_keys, answers
    dispose_of([post_key])
    dispose_of([category_key])

    dispose_of(answer_keys)
    dispose_of(tag_keys)


@pytest.fixture
def answer_keys(client_context):
    answers = {"ans1": True, "ans2": False, "ans3": False}
    return [Answer(p_answer=ans,
                               is_correct=is_correct).put()
                        for ans, is_correct in answers.items()]
