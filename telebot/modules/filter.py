from emoji import emojize
from telegram import Update
from telegram.ext import run_async, CallbackContext, CommandHandler

from telebot import dispatcher, log
from telebot.modules.sql.exceptions_sql import get_command_exception_groups
from telebot.modules.sql.filter_sql import get_filters_for_group, add_filter, del_filter


@run_async
def list_filters(update: Update, context: CallbackContext):
    log(update, "filters")

    if update.effective_chat.id in get_command_exception_groups("filter"):
        return

    filters = get_filters_for_group(update.effective_chat.id)

    if filters:
        update.message.reply_markdown("Active filters in this group are as follows -\n`" + "`\n`".join(filters) + "`")
    else:
        update.message.reply_markdown(emojize("No active filters in this group :crying_cat_face:"))


__help__ = """
/filters : list all active filters in the group
"""

__mod_name__ = "filter"

dispatcher.add_handler(CommandHandler("filters", list_filters))
