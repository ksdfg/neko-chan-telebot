from datetime import datetime
from typing import List, Union

from mongoengine import DynamicDocument, IntField, StringField, DateTimeField


# create models for this module


class Muted(DynamicDocument):
    chat = IntField(required=True)
    user = IntField(required=True)
    username = StringField(required=True)
    until_date = DateTimeField()


# create helper functions to be used to interact with the model


def add_muted_member(chat: int, user: int, username: str, until_date: datetime = None) -> bool:
    """
    Add a muted member in the db
    :param chat: chat ID that the member has been muted in
    :param user: user ID of the member
    :param username: username of the member
    :param until_date: until when he has been muted
    :return: True if successful, else False
    """
    try:
        muted_list: List[Muted] = Muted.objects(chat=chat, user=user)  # check if member is already muted

        if muted_list:
            # update existing entry
            muted_list[0].until_date = until_date
            muted_list[0].save()
        else:
            # create new entry
            Muted(chat=chat, user=user, username=username, until_date=until_date).save()

        return True

    except Exception as e:
        print(e)
        return False


def remove_muted_member(chat: int, user: int) -> bool:
    """
    Remove a muted member from db
    :param chat: chat ID in which member was muted
    :param user: user ID of member
    :return: True if successful, else false
    """
    try:
        Muted.objects(chat=chat, user=user)[0].delete()
        return True
    except IndexError:
        return True
    except Exception as e:
        print(e)
        return False


def fetch_muted_member(chat: int, username: str) -> Union[int, bool]:
    """
    Fetch user ID of muted member
    :param chat: chat ID member is muted in
    :param username: username of member
    :return: user ID of member
    """
    try:
        return Muted.objects(chat=chat, username=username)[0].user
    except IndexError:
        return False
    except Exception as e:
        print(e)
        return False
