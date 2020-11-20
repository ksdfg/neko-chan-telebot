from telegram import Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler

from telebot import dispatcher
from telebot.functions import (
    check_user_admin,
    check_bot_admin,
    bot_action,
)
from telebot.modules.db.exceptions import get_command_exception_chats
from telebot.modules.db.users import add_user


@bot_action("purge")
@check_user_admin
@check_bot_admin
def purge(update: Update, context: CallbackContext):
    """
    Delete all messages from quoted message
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    # check if user has enough perms
    if update.effective_chat.type != "private" and update.effective_chat.id not in get_command_exception_chats("admin"):
        user = update.effective_chat.get_member(update.effective_user.id)
        if not user.can_delete_messages and user.status != "creator":
            update.effective_message.reply_markdown(
                "Ask your sugar daddy to give you perms required to use the method `CanDeleteMessages`."
            )
            return

    # check if bot has perms to delete a message
    if (
        update.effective_chat.type != "private"
        and not update.effective_chat.get_member(context.bot.id).can_delete_messages
    ):
        update.effective_message.reply_text(
            "Bribe your sugar daddy with some catnip and ask him to allow me to delete messages..."
        )
        return

    # check if start point is given
    if not update.effective_message.reply_to_message:
        update.effective_message.reply_text(
            "I'm a cat, not a psychic! Reply to the message you want to start deleting from..."
        )
        return

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

    update.effective_chat.send_message("Just like we do it in china....")


__help__ = """
- /purge `<reply>` : delete all messages from replied message to current one.
"""

__mod_name__ = "Delete"

# create handlers
dispatcher.add_handler(CommandHandler("purge", purge, run_async=True))
