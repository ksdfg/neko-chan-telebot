from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

from telebot import dispatcher
from telebot.modules.db.exceptions import (
    add_command_exception_chats,
    del_command_exception_chats,
    get_exceptions_for_chat,
)
from telebot.utils import bot_action, check_user_admin, CommandDescription, check_command


@bot_action("list exceptions")
@check_command("exceptions")
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


@bot_action("add exception")
@check_command("except")
@check_user_admin
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
        print(reply)
        update.effective_message.reply_markdown(reply)


@bot_action("delete exceptions")
@check_command("delexcept")
@check_user_admin
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


__mod_name__ = "Exceptions"

__commands__ = (
    CommandDescription(command="exceptions", description="list all exceptions in chat"),
    CommandDescription(
        command="except",
        args="<commands list>",
        description="Add exceptions for given commands (space separated)",
        is_admin=True,
    ),
    CommandDescription(
        command="delexcept",
        args="<commands list>",
        description="Delete exceptions for given commands (space separated)",
        is_admin=True,
    ),
)

# create handlers
dispatcher.add_handler(CommandHandler("exceptions", list_exceptions, run_async=True))
dispatcher.add_handler(CommandHandler("except", add_exception, run_async=True))
dispatcher.add_handler(CommandHandler("delexcept", del_exception, run_async=True))
