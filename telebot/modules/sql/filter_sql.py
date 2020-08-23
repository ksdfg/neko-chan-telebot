from mongoengine import Document, IntField, StringField


# create models for this module


class Filter(Document):
    chat = IntField()
    trigger = StringField()
    content = StringField()
    filter_type = StringField(choices=('text', 'sticker', 'document', 'photo', 'audio', 'voice', 'video'))


# create helper functions to be used to interact with the model


def get_triggers_for_chat(chat):
    try:
        return [f.trigger for f in Filter.objects(chat=chat)]
    except:
        return []


def get_filter(chat, trigger):
    try:
        return Filter.objects(chat=chat, trigger=trigger)[0]
    except:
        return None


def add_filter(chat, trigger, content, filter_type):
    try:
        filter_list = Filter.objects(chat=chat, trigger=trigger)

        if filter_list:
            f = filter_list[0]
            f.content = content
            f.filter_type = filter_type
            f.save()
        else:
            Filter(chat=chat, trigger=trigger, content=content, filter_type=filter_type).save()

        return f"I'm now going to meow everytime someone says `{trigger}`.... meow"
    except:
        return (
            f"Couldn't save the filter.... bribe my owner with some catnip and see if he can find the bug, or try again"
        )


def del_filter(chat, trigger):
    try:
        filter_list = Filter.objects(chat=chat, trigger=trigger)
        if filter_list:
            filter_list[0].delete()
            return f"I'm now going to stop meowing everytime someone says `{trigger}`.... meow"
        else:
            return f"Oi, you can't make me stop meowing if I'm not meowing in the first place. There's no filter for `{trigger}`, baka!"
    except:
        return f"Couldn't delete the filter.... bribe my owner with some catnip and see if he can find the bug, or try again"
