from typing import List, Tuple, Optional

from emoji import emojize
from mongoengine import StringField, DynamicDocument, IntField


# create models for this module


class Note(DynamicDocument):
    chat = IntField()  # chat ID in which note is to be added
    name = StringField()  # name by which the note will be referred to
    content = StringField()  # content stored within that note
    content_type = StringField(choices=("text", "sticker", "document", "photo", "audio", "voice", "video"))


# create helper functions to be used to interact with the model


def get_notes_for_chat(chat: int) -> List[str]:
    """
    Get all the names of the notes in given chat
    :param chat: chat ID whose notes we're fetching
    :return: list of all the names of the notes
    """
    try:
        return [n.name for n in Note.objects(chat=chat)]
    except:
        return []


def get_note(chat: int, name: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Get the content and content type of the given note
    :param chat: chat ID the note is in
    :param name: name of the note
    :return: content to be sent as a reply, type of that content
    """
    try:
        note: Note = Note.objects(chat=chat, name=name)[0]
        return note.content, note.content_type
    except:
        return None, None


def add_note(chat: int, name: str, content: str, content_type: str) -> str:
    """
    Add a note to the db
    :param chat: the chat ID in which the note is to be added
    :param name: the name of the note
    :param content: content stored within the note
    :param content_type: type of the content
    :return: Message to be sent to the user
    """
    try:
        note_list: List[Note] = Note.objects(chat=chat, name=name)

        if note_list:
            # if note for given name exists in given chat, then update that note
            f: Note = note_list[0]
            f.content = content
            f.content_type = content_type
            f.save()
        else:
            # if no note exists for given name in given chat, then make one
            Note(chat=chat, name=name, content=content, content_type=content_type).save()

        return emojize(
            f"Ok, I'll remember this note as `{name}`....\n"
            "unless I need to free memory to store more cat videos :grinning_cat_face:"
        )

    except:
        return (
            f"Couldn't save the note.... bribe my owner with some catnip and see if he can find the bug, or try again"
        )


def del_note(chat: int, name: str) -> str:
    """
    Delete a note in a chat
    :param chat: chat ID in which the note currently exists
    :param name: keyword that currently names the note
    :return: reply to be given to the user in Telegram
    """
    try:
        note_list: List[Note] = Note.objects(chat=chat, name=name)

        if note_list:
            # if the note exists
            note_list[0].delete()
            return f"I've forgotten about the note `{name}`.... sorry, what were we talking about?"
        else:
            # if no such note exists
            return f"Oi, you can't make me forget something I don't remember. There's no note for `{name}`, baka!"

    except:
        return (
            f"Couldn't delete the note.... bribe my owner with some catnip and see if he can find the bug, or try again"
        )
