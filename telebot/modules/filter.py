from re import IGNORECASE, search, escape

from emoji import emojize
from telegram import Update
from telegram.ext import run_async, CallbackContext, CommandHandler, MessageHandler, Filters

from telebot import dispatcher
from telebot.functions import log
from telebot.modules.db.exceptions import get_command_exception_chats
from telebot.modules.db.filter import get_triggers_for_chat, add_filter, get_filter, del_filter


@run_async
def list_filters(update: Update, context: CallbackContext) -> None:
    """
    List all the filter triggers in a chat
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    # check for exception
    if update.effective_chat.id in get_command_exception_chats("filter"):
        return

    log(update, "filters")

    filters = get_triggers_for_chat(update.effective_chat.id)
    if filters:
        update.message.reply_markdown(
            "Active filter triggers in this chat are as follows -\n`" + "`\n`".join(filters) + "`"
        )
    else:
        update.message.reply_markdown(emojize("No active filters in this chat :crying_cat_face:"))


@run_async
def add_filter_handler(update: Update, context: CallbackContext) -> None:
    """
    Add a filter in a chat
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    # check for exception
    if update.effective_chat.id in get_command_exception_chats("filter"):
        return

    log(update, "addfilter")

    # for ease of reference
    msg = update.effective_message

    # get trigger and content from the message
    try:
        trigger, content = msg.text_markdown.split(None, 2)[1:]
    except ValueError:
        try:
            trigger = msg.text.split()[1]
            content = None
        except IndexError:
            msg.reply_markdown("No trigger, No content....\n\nYou could've at least come with some catnip\n`._.`")
            return

    # set kwargs to be passed to add_filter function
    kwargs = {'chat': update.effective_chat.id, 'trigger': trigger}

    # add content and filter type to kwargs

    if content is not None:
        kwargs['content'] = content
        kwargs['filter_type'] = "text"

    elif msg.reply_to_message and msg.reply_to_message.sticker:
        kwargs['content'] = msg.reply_to_message.sticker.file_id
        kwargs['filter_type'] = "sticker"

    elif msg.reply_to_message and msg.reply_to_message.document:
        kwargs['content'] = msg.reply_to_message.document.file_id
        kwargs['filter_type'] = "document"

    elif msg.reply_to_message and msg.reply_to_message.photo:
        kwargs['content'] = msg.reply_to_message.photo[-1].file_id
        kwargs['filter_type'] = "photo"

    elif msg.reply_to_message and msg.reply_to_message.audio:
        kwargs['content'] = msg.reply_to_message.audio.file_id
        kwargs['filter_type'] = "audio"

    elif msg.reply_to_message and msg.reply_to_message.voice:
        kwargs['content'] = msg.reply_to_message.voice.file_id
        kwargs['filter_type'] = "voice"

    elif msg.reply_to_message and msg.reply_to_message.video:
        kwargs['content'] = msg.reply_to_message.video.file_id
        kwargs['filter_type'] = "video"

    else:
        msg.reply_markdown("This cat isn't a random reply generator, baka! Give some content to reply with......")
        return

    # add filter in DB
    msg.reply_markdown(add_filter(**kwargs))


@run_async
def del_filter_handler(update: Update, context: CallbackContext) -> None:
    """
    Delete a filter from the chat
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    # check for exception
    if update.effective_chat.id in get_command_exception_chats("filter"):
        return

    log(update, "del filter")

    if context.args:
        # iterate over the triggers given and delete them from DB
        for trigger in context.args:
            update.effective_message.reply_markdown(del_filter(chat=update.effective_chat.id, trigger=trigger))
    else:
        update.effective_message.reply_markdown(
            "I can't stop meowing if you don't tell me what to stop meowing to, baka!"
        )


@run_async
def reply(update: Update, context: CallbackContext) -> None:
    """
    Reply when a filter is triggered
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    # check for exception
    if update.effective_chat.id in get_command_exception_chats("filter"):
        return

    # check if there is any text to check
    msg = update.effective_message
    text = msg.caption if msg.text is None else msg.text
    if text is None:
        return

    # get triggers for the chat
    triggers = get_triggers_for_chat(update.effective_chat.id)

    for trigger in triggers:
        pattern = r"( |^|[^\w])" + escape(trigger) + r"( |$|[^\w])"  # regex for text containing the trigger

        if search(pattern, text, flags=IGNORECASE):
            log(update, f"reply to filter trigger `{trigger}`")

            # get content and type to reply in response to trigger
            content, filter_type = get_filter(update.effective_chat.id, trigger)

            # send reply according to type
            if filter_type == "text":
                msg.reply_markdown(content)
            elif filter_type == "sticker":
                msg.reply_sticker(content)
            elif filter_type == "document":
                msg.reply_document(content)
            elif filter_type == "photo":
                msg.reply_photo(content)
            elif filter_type == "audio":
                msg.reply_audio(content)
            elif filter_type == "voice":
                msg.reply_voice(content)
            elif filter_type == "video":
                msg.reply_video(content)

            break


__help__ = """
- /filters : list all active filters in the chat

- /addfilter `<trigger> [<content>|<reply>]` : add a filter

- /delfilters `<triggers list>` : delete active filters; give all filters to delete seperated by a space.

If you add an exception for `filter` in the chat, it will make sure that none of these commands do anything. Adding exceptions for individual commands has no effect.
"""

__mod_name__ = "Filters"

dispatcher.add_handler(CommandHandler("filters", list_filters))
dispatcher.add_handler(CommandHandler("addfilter", add_filter_handler))
dispatcher.add_handler(CommandHandler("delfilters", del_filter_handler))
dispatcher.add_handler(MessageHandler(Filters.all, reply), group=69)
