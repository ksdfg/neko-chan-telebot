from telegram import Update
from telegram.ext import run_async, CallbackContext, CommandHandler, MessageHandler, Filters

from telebot import log, dispatcher
from telebot.modules.db.exceptions import get_command_exception_chats
from telebot.modules.db.notes import get_note


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
    if content is None:
        update.effective_message.reply_text("No such note in my memory...")
    elif content_type == "text":
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


__help__ = """
- /get <note name>: get the note with this note name
- #<note name>: same as /get
- /notes or /saved: list all saved notes in this chat
 
*Admin only:*
- /save `<note name> <reply|note data>`: saves replied message or `note data` as a note with name `note name`.
- /clear <note name>: clear note with this name

**If you add an exception for `notes` in the chat, it will make sure that none of these commands do anything. Adding exceptions for individual commands has no effect.**
"""

__mod_name__ = "Notes"

dispatcher.add_handler(CommandHandler("get", fetch_note))
dispatcher.add_handler(MessageHandler(Filters.regex(r"^#[^\s]+$"), fetch_note))
