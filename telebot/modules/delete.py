from functools import wraps
from re import match
from traceback import print_exc
from typing import Callable

from telegram import Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler

from telebot import dispatcher
from telebot.modules.db.exceptions import get_command_exception_chats
from telebot.modules.db.users import add_user
from telebot.utils import (
    check_user_admin,
    check_bot_admin,
    bot_action,
    check_reply_to_message,
    CommandDescription,
)


def check_bot_can_delete(func: Callable):
    """
    Wrapper function for checking if bot can delete messages
    :param func: The function this wraps over
    """

    @wraps(func)
    def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        # check if bot has perms to delete a message
        if (
            update.effective_chat.type != "private"
            and not update.effective_chat.get_member(context.bot.id).can_delete_messages
        ):
            update.effective_message.reply_text(
                "Bribe your sugar daddy with some catnip and ask him to allow me to delete messages..."
            )
            return

        return func(update, context, *args, **kwargs)

    return wrapper


def check_user_can_delete(func: Callable):
    """
    Wrapper function for checking if user can delete messages
    :param func: The function this wraps over
    """

    @wraps(func)
    def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        # check if user can delete messages
        if (
            update.effective_chat.type != "private"
            and update.effective_message.reply_to_message.from_user.id != update.effective_user.id
            and update.effective_chat.id not in get_command_exception_chats("delete")
        ):
            user = update.effective_chat.get_member(update.effective_user.id)
            if not user.can_delete_messages and user.status != "creator":
                update.effective_message.reply_markdown(
                    "Ask your sugar daddy to give you perms required to use the method `CanDeleteMessages`, "
                    "or add an exception to module `delete`."
                )
                return

        return func(update, context, *args, **kwargs)

    return wrapper


@bot_action("delete")
@check_reply_to_message(error_msg="I'm a cat, not a psychic! Reply to the message you want to delete...")
@check_user_admin
@check_user_can_delete
@check_bot_admin
@check_bot_can_delete
def delete(update: Update, context: CallbackContext):
    """
    Delete the quoted message
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """

    # for future usage
    add_user(
        user_id=update.effective_message.reply_to_message.from_user.id,
        username=update.effective_message.reply_to_message.from_user.username,
    )

    # delete message
    try:
        context.bot.delete_message(update.effective_chat.id, update.effective_message.reply_to_message.message_id)
        context.bot.delete_message(update.effective_chat.id, update.effective_message.message_id)
    except BadRequest as e:
        if match("^Message can't be deleted", e.message):
            print_exc()
            update.effective_message.reply_text(
                "I don't know why but I can't delete that...\nTelegram is high on catnip as usual."
            )
        else:
            raise e


@bot_action("purge")
@check_user_admin
@check_reply_to_message(error_msg="I'm a cat, not a psychic! Reply to the message you want to start deleting from...")
@check_user_can_delete
@check_bot_admin
@check_bot_can_delete
def purge(update: Update, context: CallbackContext):
    """
    Delete all messages from quoted message
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    # for future usage
    add_user(
        user_id=update.effective_message.reply_to_message.from_user.id,
        username=update.effective_message.reply_to_message.from_user.username,
    )

    # delete messages
    for id_ in range(update.effective_message.message_id, update.effective_message.reply_to_message.message_id - 1, -1):
        try:
            context.bot.delete_message(update.effective_chat.id, id_)
        except BadRequest:
            continue

    # Don't send message after purge if silent/quiet is specified
    if not (context.args and context.args[0].lower() in ("silent", "quiet")):
        update.effective_chat.send_message("Just like we do it in china....")


__help__ = """
- /del `<reply>` : delete the quoted message.
- /purge `<reply> [silent|quiet]` : delete all messages from replied message to current one.

If you add an exception to `delete`, I will allow admins to execute commands even if they don't have the permission to delete messages.
"""

__mod_name__ = "Delete"

__exception_desc__ = (
    "If you add an exception to `delete`, I will allow admins to execute commands even if they don't have the "
    "permission to delete messages."
)

__commands__ = [
    CommandDescription(command="del", args="<reply>", description="delete the quoted message"),
    CommandDescription(command="purge", args="<reply> [silent|quiet]", description="delete the quoted message"),
]

# create handlers
dispatcher.add_handler(CommandHandler("del", delete, run_async=True))
dispatcher.add_handler(CommandHandler("delete", delete, run_async=True))
dispatcher.add_handler(CommandHandler("purge", purge, run_async=True))
