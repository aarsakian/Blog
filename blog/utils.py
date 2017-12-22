from urlparse import urljoin


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


def datetimeformat(value, format='%H:%M / %A-%B-%Y'):
    return value.strftime(format)

def make_external(base_url, url):
    return urljoin(base_url, url)
