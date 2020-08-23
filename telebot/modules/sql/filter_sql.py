from mongoengine import Document, IntField, StringField


# create models for this module


class Filter(Document):
    group = IntField()
    keyword = StringField()
    content = StringField()
    filter_type = StringField(choices=('text', 'sticker', 'document', 'photo', 'audio', 'voice', 'video'))


# create helper functions to be used to interact with the model


def get_filters_for_group(group_id):
    try:
        return [f.keyword for f in Filter.objects(group=group_id)]
    except:
        return []


def add_filter(group, keyword, content, filter_type):
    try:
        Filter(group=group, keyword=keyword, content=content, filter_type=filter_type).save()
        return True
    except:
        return False


def del_filter(group, keyword):
    try:
        filter_list = Filter.objects(group=group, keyword=keyword)
        if filter_list:
            filter_list[0].delete()
            return True
        else:
            return True
    except:
        return False
