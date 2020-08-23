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


def get_filter(group_id, keyword):
    try:
        return Filter.objects(group=group_id, keyword=keyword)[0]
    except:
        return None


def add_filter(group, keyword, content, filter_type):
    try:
        filter_list = Filter.objects(group=group, keyword=keyword)

        if filter_list:
            f = filter_list[0]
            f.content = content
            f.filter_type = filter_type
            f.save()
        else:
            Filter(group=group, keyword=keyword, content=content, filter_type=filter_type).save()

        return f"I'm now going to meow everytime someone says `{keyword}`.... meow"
    except:
        return (
            f"Couldn't save the filter.... bribe my owner with some catnip and see if he can find the bug, or try again"
        )


def del_filter(group, keyword):
    try:
        filter_list = Filter.objects(group=group, keyword=keyword)
        if filter_list:
            filter_list[0].delete()
            return f"I'm now going to stop meowing everytime someone says `{keyword}`.... meow"
        else:
            return f"Oi, you can't make me stop meowing if I'm not meowing in the first place. There's no filter for `{keyword}`, baka!"
    except:
        return f"Couldn't delete the filter.... bribe my owner with some catnip and see if he can find the bug, or try again"
