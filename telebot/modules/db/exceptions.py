from copy import deepcopy
from typing import List

from mongoengine import Document, StringField, ListField, IntField


# create models for this module
from telegram.utils.helpers import escape_markdown


class Exceptions(Document):
    command = StringField(required=True)  # bot_action for which exception is being set
    chats = ListField(IntField())  # list of chat IDs in which exception is being set


# create helper functions to be used to interact with the model


def get_command_exception_chats(command: str) -> List[int]:
    """
    Get all chats that have an exception for a given bot_action
    :param command: the bot_action whose exception we're checking for
    :return: list of chat IDs
    """
    exceptions: List[Exceptions] = Exceptions.objects(command=command)

    if exceptions:
        return exceptions[0].chats
    else:
        return []


def add_command_exception_chats(command: str, chat: int) -> str:
    """
    Add exception for a bot_action in a chat
    :param command: the bot_action for which we're adding an exception
    :param chat: the chat ID in which we're adding the exception
    :return: the message to be replied to the user in Telegram
    """
    exceptions_list: List[Exceptions] = Exceptions.objects(command=command)

    # if exceptions document for bot_action exists
    if exceptions_list:
        exceptions: Exceptions = exceptions_list[0]
        if chat in exceptions.chats:
            return f" Exception for bot action `{escape_markdown(command)}` already added!"
        else:
            exceptions.chats = exceptions.chats + [chat]
            exceptions.save()

    # if exceptions document doesn't exist for the bot_action
    else:
        Exceptions(command=command, chats=[chat]).save()

    return f" Exception for bot action `{escape_markdown(command)}` added!"


def del_command_exception_chats(command: str, chat: int) -> str:
    """
    delete exception for a bot_action in a chat
    :param command: the bot_action for which we're deleting an exception
    :param chat: the chat ID in which we're deleting the exception
    :return: the message to be replied to the user in Telegram
    """
    exceptions_list: List[Exceptions] = Exceptions.objects(command=command)

    if exceptions_list:
        exceptions: Exceptions = exceptions_list[0]

        # delete exception
        try:
            chats: List[int] = deepcopy(exceptions.chats)
            chats.remove(chat)
            if chats:
                # if there are other chats in which this exception exists
                exceptions.chats = chats
                exceptions.save()
            else:
                # if there are no other chats in which this exception exists
                exceptions.delete()

            return f" Exception for bot action `{escape_markdown(command)}` deleted!"

        except ValueError:
            # if the given chat ID isn't in the list of chats with exception for given bot_action
            return f" Exception for bot action `{escape_markdown(command)}` not added!"

    else:
        # if there is no exceptions document for this bot_action
        return f" Exception for bot action `{escape_markdown(command)}` not added!"


def get_exceptions_for_chat(chat: int) -> List[str]:
    """
    Get all the commands for which an exception is added in a chat
    :param chat: chat ID whose exceptions we're fetching
    :return: list of all the commands for which an exception is added
    """
    exceptions: List[Exceptions] = Exceptions.objects(chats=chat)

    if exceptions:
        return [x.command for x in exceptions]
    else:
        return []
