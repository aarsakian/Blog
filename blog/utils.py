
def find_tags_to_be_deleted_from_an_edited_post(editing_tags, existing_tags):
    tag_to_kept = set(editing_tags) & set(existing_tags)
    return set(existing_tags)-tag_to_kept