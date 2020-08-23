from copy import deepcopy

from mongoengine import Document, StringField, ListField, IntField


# create models for this module
class Exceptions(Document):
    command = StringField(required=True)
    chats = ListField(IntField())


"""
create helper functions to be used to interact with the model
"""


def get_command_exception_chats(command: str) -> list:
    exceptions = Exceptions.objects(command=command)

    if exceptions:
        return exceptions[0].chats
    else:
        return []


def add_command_exception_chats(command: str, chat: int) -> str:
    exceptions_list = Exceptions.objects(command=command)

    if exceptions_list:
        exceptions = exceptions_list[0]
        if chat in exceptions.chats:
            return f"Exception for command `{command}` already added!"
        else:
            exceptions.chats = exceptions.chats + [chat]
            exceptions.save()

    else:
        Exceptions(command=command, chats=[chat]).save()

    return f"Exception for command `{command}` added!"


def del_command_exception_chats(command: str, chat: int) -> str:
    exceptions_list = Exceptions.objects(command=command)

    if exceptions_list:
        exceptions = exceptions_list[0]
        try:
            chats = deepcopy(exceptions.chats)
            chats.remove(chat)
            if chats:
                exceptions.chats = chats
                exceptions.save()
            else:
                exceptions.delete()

            return f"Exception for command `{command}` deleted!"

        except ValueError:
            return f"Exception for command `{command}` not added!"

    else:
        return f"Exception for command `{command}` not added!"


def get_exceptions_for_chat(chat: int) -> list:
    exceptions = Exceptions.objects(chats=chat)

    if exceptions:
        return [x.command for x in exceptions]
    else:
        return []
