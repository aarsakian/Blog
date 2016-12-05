
def find_tags_to_be_deleted_from_an_edited_post(editing_tags, existing_tags):
    tag_to_kept = set(editing_tags) & set(existing_tags)
    return set(existing_tags)-tag_to_kept


def find_tags_to_added_from_an_edited_post(editing_tags, existing_tags):
    return set(editing_tags) ^ set(editing_tags) & set(existing_tags)


def find_new_post_tags(old_post_tags, tags_to_be_deleted, tags_to_be_added):
    return (set(old_post_tags) - tags_to_be_deleted) ^ tags_to_be_added