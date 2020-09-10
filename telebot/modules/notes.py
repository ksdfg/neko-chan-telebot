from emoji import emojize
from telegram import Update
from telegram.ext import run_async, CallbackContext, CommandHandler, MessageHandler, Filters

from telebot import dispatcher
from telebot.functions import log, check_user_admin
from telebot.modules.db.exceptions import get_command_exception_chats
from telebot.modules.db.notes import get_note, get_notes_for_chat, add_note, del_note


@run_async
def fetch_note(update: Update, context: CallbackContext):
    """
    Fetch note
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    # check exception
    if update.effective_chat.id in get_command_exception_chats("notes"):
        return

    log(update, "get note")

    if update.effective_message.text[0] == "#":
        name = update.effective_message.text[1:]
    elif context.args:
        name = context.args[0]
    else:
        update.effective_message.reply_text("I can't fetch a note if you don't tell me it's name, baka!")
        return

    # get note
    content, content_type = get_note(update.effective_chat.id, name)

    # send reply according to type
    if content_type == "text":
        update.effective_message.reply_markdown(content)
    elif content_type == "sticker":
        update.effective_message.reply_sticker(content)
    elif content_type == "document":
        update.effective_message.reply_document(content)
    elif content_type == "photo":
        update.effective_message.reply_photo(content)
    elif content_type == "audio":
        update.effective_message.reply_audio(content)
    elif content_type == "voice":
        update.effective_message.reply_voice(content)
    elif content_type == "video":
        update.effective_message.reply_video(content)


@run_async
def notes_for_chat(update: Update, context: CallbackContext):
    """
    List out all the notes in a chat
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    # check exception
    if update.effective_chat.id in get_command_exception_chats("notes"):
        return

    log(update, "notes")

    # get list of notes for the chat
    notes = get_notes_for_chat(update.effective_chat.id)

    if notes:
        reply = "***Saved notes in chat***"
        for note in notes:
            reply += f"\n- `{note}`"
        reply += emojize("\n\nI remember all of this! Praise me lots! :grinning_cat_face:")

        update.effective_message.reply_markdown(reply)

    else:
        update.effective_message.reply_text("No one told me to remember anything, so I got high on catnip instead.....")


@run_async
@check_user_admin
def add_note_in_chat(update: Update, context: CallbackContext):
    """
    Add a note in the chat
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    # check exception
    if update.effective_chat.id in get_command_exception_chats("notes"):
        return

    # for ease of reference
    msg = update.effective_message

    # get name and content from the message
    try:
        name, content = msg.text_markdown.split(None, 2)[1:]
    except ValueError:
        try:
            name = context.args[0]
            content = None
        except IndexError:
            msg.reply_markdown("No name, No content....\n\nYou could've at least come with some catnip\n`._.`")
            return

    # set kwargs to be passed to add_note function
    kwargs = {'chat': update.effective_chat.id, 'name': name}

    # add content and content type to kwargs

    if content is not None:
        kwargs['content'] = content
        kwargs['content_type'] = "text"

    elif msg.reply_to_message and msg.reply_to_message.text_markdown:
        kwargs['content'] = msg.reply_to_message.text_markdown
        kwargs['content_type'] = "text"

    elif msg.reply_to_message and msg.reply_to_message.sticker:
        kwargs['content'] = msg.reply_to_message.sticker.file_id
        kwargs['content_type'] = "sticker"

    elif msg.reply_to_message and msg.reply_to_message.document:
        kwargs['content'] = msg.reply_to_message.document.file_id
        kwargs['content_type'] = "document"

    elif msg.reply_to_message and msg.reply_to_message.photo:
        kwargs['content'] = msg.reply_to_message.photo[-1].file_id
        kwargs['content_type'] = "photo"

    elif msg.reply_to_message and msg.reply_to_message.audio:
        kwargs['content'] = msg.reply_to_message.audio.file_id
        kwargs['content_type'] = "audio"

    elif msg.reply_to_message and msg.reply_to_message.voice:
        kwargs['content'] = msg.reply_to_message.voice.file_id
        kwargs['content_type'] = "voice"

    elif msg.reply_to_message and msg.reply_to_message.video:
        kwargs['content'] = msg.reply_to_message.video.file_id
        kwargs['content_type'] = "video"

    else:
        msg.reply_markdown("This cat isn't a random note generator, baka! Give some content to remember......")
        return

    # save note and reply to user
    msg.reply_markdown(add_note(**kwargs))


@run_async
@check_user_admin
def del_note_in_chat(update: Update, context: CallbackContext):
    """
    Delete a note from the chat
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    # check for exception
    if update.effective_chat.id in get_command_exception_chats("notes"):
        return

    log(update, "del note")

    if context.args:
        # iterate over the triggers given and delete them from DB
        for name in context.args:
            update.effective_message.reply_markdown(del_note(chat=update.effective_chat.id, name=name))
    else:
        update.effective_message.reply_markdown(
            "Oi, you can't make me forget something without reminding me of what to forget, baka!"
        )


__help__ = """
- /get <note name>: get the note with this note name

- `#<note name>`: same as /get

- /notes or /saved: list all saved notes in this chat
 
***Admin only :***

- /save `<note name> <reply|note data>`: saves replied message or `note data` as a note with name `note name`.

- /clear <note names list>: clear note with this name

If you add an exception for `notes` in the chat, it will make sure that none of these commands do anything. Adding exceptions for individual commands has no effect.
"""

__mod_name__ = "Notes"

dispatcher.add_handler(CommandHandler("get", fetch_note))
dispatcher.add_handler(MessageHandler(Filters.regex(r"^#[^\s]+$"), fetch_note))
dispatcher.add_handler(CommandHandler("notes", notes_for_chat))
dispatcher.add_handler(CommandHandler("saved", notes_for_chat))
dispatcher.add_handler(CommandHandler("save", add_note_in_chat))
dispatcher.add_handler(CommandHandler("clear", del_note_in_chat))
