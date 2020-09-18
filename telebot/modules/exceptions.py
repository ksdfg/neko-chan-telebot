from telegram import Update
from telegram.ext import CommandHandler, run_async, CallbackContext

from telebot import dispatcher
from telebot.functions import log, bot_action
from telebot.modules.db.exceptions import (
    add_command_exception_chats,
    del_command_exception_chats,
    get_exceptions_for_chat,
)


@run_async
@bot_action()
def list_exceptions(update: Update, context: CallbackContext):
    """
    List all exceptions
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    if update.effective_chat.type == "private":
        update.effective_message.reply_text("You can't list exceptions in private chats.")
        return

    commands = ", ".join(get_exceptions_for_chat(update.effective_chat.id))
    if commands:
        update.effective_message.reply_markdown(f"You have exceptions set for the following commands:\n`{commands}`")
    else:
        update.effective_message.reply_text("You don't have any exceptions set!")


@run_async
@bot_action("add exception")
def add_exception(update: Update, context: CallbackContext):
    """
    Add exceptions in a chat
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    if update.effective_chat.type == "private":
        update.effective_message.reply_text("You can't add exceptions in private chats.")
        return

    for command in context.args:
        reply = add_command_exception_chats(command, update.effective_chat.id)
        update.effective_message.reply_markdown(reply)


@run_async
@bot_action("delete exceptions")
def del_exception(update: Update, context: CallbackContext):
    """
    Delete exceptions in a chat
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    if update.effective_chat.type == "private":
        update.effective_message.reply_text("You can't delete exceptions in private chats.")
        return

    for command in context.args:
        reply = del_command_exception_chats(command, update.effective_chat.id)
        update.effective_message.reply_markdown(reply)


__help__ = """
Adding an exception for a bot_action in your chat will change it's behaviour. How it will change depends on the bot_action.

- /listexceptions : list all exceptions in chat

- /addexceptions `<commands list>` : Add exceptions for given commands (space separated)

- /delexceptions `<commands list>` : Delete exceptions for given commands (space separated)
"""

__mod_name__ = "Exceptions"

# create handlers
dispatcher.add_handler(CommandHandler('listexceptions', list_exceptions))
dispatcher.add_handler(CommandHandler('addexceptions', add_exception))
dispatcher.add_handler(CommandHandler('delexceptions', del_exception))
