from typing import List, Optional, Tuple

from mongoengine import Document, IntField, StringField


# create models for this module


class Filter(Document):
    chat = IntField()  # chat ID in which filter is set
    trigger = StringField()  # keyword which will trigger the filter to reply
    content = StringField()  # what to reply on being triggered
    filter_type = StringField(choices=("text", "sticker", "document", "photo", "audio", "voice", "video"))


# create helper functions to be used to interact with the model


def get_triggers_for_chat(chat) -> List[str]:
    """
    Get all the keywords that trigger a filter in given chat
    :param chat: chat ID whose filter triggers we're fetching
    :return: list of all the triggers
    """
    try:
        return [f.trigger for f in Filter.objects(chat=chat)]
    except:
        return []


def get_filter(chat, trigger) -> Tuple[Optional[str], Optional[str]]:
    """
    Get the content and filter type of the given filter
    :param chat: chat ID the filter is applied in
    :param trigger: trigger keyword of the filter
    :return: content to be sent as a reply, type of that content
    """
    try:
        _filter: Filter = Filter.objects(chat=chat, trigger=trigger)[0]
        return _filter.content, _filter.filter_type
    except:
        return None, None


def add_filter(chat, trigger, content, filter_type) -> str:
    """
    Add a filter in a chat
    :param chat: chat ID in which to add filter
    :param trigger: keyword that will trigger the filter
    :param content: content to be sent as a reply on trigger
    :param filter_type: the type of the content
    :return: string to be replied to the user in Telegram
    """
    try:
        filter_list: List[Filter] = Filter.objects(chat=chat, trigger=trigger)

        if filter_list:
            # if filter for given trigger exists in given chat, then update that filter
            f: Filter = filter_list[0]
            f.content = content
            f.filter_type = filter_type
            f.save()
        else:
            # if no filter exists for given trigger in given chat, then make one
            Filter(chat=chat, trigger=trigger, content=content, filter_type=filter_type).save()

        return f"I'm now going to meow everytime someone says `{trigger}`.... meow"

    except:
        return (
            f"Couldn't save the filter.... bribe my owner with some catnip and see if he can find the bug, or try again"
        )


def del_filter(chat, trigger) -> str:
    """
    Delete a filter in a chat
    :param chat: chat ID in which the filter currently exists
    :param trigger: keyword that currently triggers the filter
    :return: reply to be given to the user in Telegram
    """
    try:
        filter_list: List[Filter] = Filter.objects(chat=chat, trigger=trigger)

        if filter_list:
            # if the filter exists
            filter_list[0].delete()
            return f"I'm now going to stop meowing everytime someone says `{trigger}`.... meow"
        else:
            # if no such filter exists
            return f"Oi, you can't make me stop meowing if I'm not meowing in the first place. There's no filter for `{trigger}`, baka!"

    except:
        return f"Couldn't delete the filter.... bribe my owner with some catnip and see if he can find the bug, or try again"
