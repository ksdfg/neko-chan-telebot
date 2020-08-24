from re import IGNORECASE, search, escape

from emoji import emojize
from telegram import Update
from telegram.ext import run_async, CallbackContext, CommandHandler, MessageHandler, Filters

from telebot import dispatcher, log
from telebot.modules.sql.exceptions_sql import get_command_exception_chats
from telebot.modules.sql.filter_sql import get_triggers_for_chat, add_filter, get_filter, del_filter


@run_async
def list_filters(update: Update, context: CallbackContext):
    log(update, "filters")

    if update.effective_chat.id in get_command_exception_chats("filter"):
        return

    filters = get_triggers_for_chat(update.effective_chat.id)

    if filters:
        update.message.reply_markdown("Active filters in this chat are as follows -\n`" + "`\n`".join(filters) + "`")
    else:
        update.message.reply_markdown(emojize("No active filters in this chat :crying_cat_face:"))


@run_async
def add_filter_handler(update: Update, context: CallbackContext):
    log(update, "addfilter")

    if update.effective_chat.id in get_command_exception_chats("filter"):
        return

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

    msg.reply_markdown(add_filter(**kwargs))


@run_async
def del_filter_handler(update: Update, context: CallbackContext):
    log(update, "del filter")

    if update.effective_chat.id in get_command_exception_chats("filter"):
        return

    if context.args:
        for trigger in context.args:
            update.effective_message.reply_markdown(del_filter(chat=update.effective_chat.id, trigger=trigger))
    else:
        update.effective_message.reply_markdown(
            "I can't stop meowing if you don't tell me what to stop meowing to, baka!"
        )


@run_async
def reply(update: Update, context: CallbackContext):
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
        pattern = r"( |^|[^\w])" + escape(trigger) + r"( |$|[^\w])"

        if search(pattern, text, flags=IGNORECASE):
            log(update, f"reply to filter trigger `{trigger}`")
            _filter = get_filter(update.effective_chat.id, trigger)

            if _filter.filter_type == "text":
                msg.reply_markdown(_filter.content)
            elif _filter.filter_type == "sticker":
                msg.reply_sticker(_filter.content)
            elif _filter.filter_type == "document":
                msg.reply_document(_filter.content)
            elif _filter.filter_type == "photo":
                msg.reply_photo(_filter.content)
            elif _filter.filter_type == "audio":
                msg.reply_audio(_filter.content)
            elif _filter.filter_type == "voice":
                msg.reply_voice(_filter.content)
            elif _filter.filter_type == "video":
                msg.reply_video(_filter.content)

            break


__help__ = """
/filters : list all active filters in the chat
/addfilter <trigger> [<content>|<reply>] : add a filter
/delfilters <triggers list> : delete active filters; give all filters to delete seperated by a space
"""

__mod_name__ = "Filters"

dispatcher.add_handler(CommandHandler("filters", list_filters))
dispatcher.add_handler(CommandHandler("addfilter", add_filter_handler))
dispatcher.add_handler(CommandHandler("delfilters", del_filter_handler))
dispatcher.add_handler(MessageHandler(Filters.all, reply), group=69)
