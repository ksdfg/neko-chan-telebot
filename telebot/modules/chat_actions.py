from telegram import Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler

from telebot import dispatcher
from telebot.functions import log, check_bot_admin


@check_bot_admin
def pin(update: Update, context: CallbackContext):
    """
    Pin a message in the chat
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    # check if bot has perms to pin a message
    if (
        update.effective_chat.type == "supergroup"
        and not update.effective_chat.get_member(context.bot.id).can_pin_messages
    ) or (
        update.effective_chat.type == "channel"
        and not update.effective_chat.get_member(context.bot.id).can_edit_messages
    ):
        update.effective_message.reply_text(
            "Bribe your sugar daddy with some catnip and ask him to allow me to pin messages..."
        )
        return

    log(update, "pin")

    # check if there is a message to pin
    if not update.effective_message.reply_to_message:
        update.effective_message.reply_text("I'm a cat, not a psychic! Reply to the message you want to pin...")
        return

    # Don't always loud pin
    if context.args:
        disable_notification = context.args[0].lower() in ('silent', 'quiet')

    # pin the message
    context.bot.pin_chat_message(
        update.effective_chat.id,
        update.effective_message.reply_to_message.message_id,
        disable_notification=disable_notification,
    )


@check_bot_admin
def purge(update: Update, context: CallbackContext):
    """
    Delete all messages from quoted message
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    # check if bot has perms to delete a message
    if (
        update.effective_chat.type != "private"
        and not update.effective_chat.get_member(context.bot.id).can_delete_messages
    ):
        update.effective_message.reply_text(
            "Bribe your sugar daddy with some catnip and ask him to allow me to delete messages..."
        )
        return

    log(update, "purge")

    # check if start point is given
    if not update.effective_message.reply_to_message:
        update.effective_message.reply_text(
            "I'm a cat, not a psychic! Reply to the message you want to start deleting from..."
        )
        return

    # delete messages
    for id_ in range(
        update.effective_message.message_id - 1, update.effective_message.reply_to_message.message_id - 1, -1
    ):
        try:
            context.bot.delete_message(update.effective_chat.id, id_)
        except BadRequest:
            continue

    update.effective_message.reply_text("Just like we do it in china....")


__mod_name__ = "Chat-Actions"

__help__ = """
- /purge `<reply>` : delete all messages from replied message to current one.
- /pin `<reply>` : pin replied message in the chat.
"""

# create handlers
dispatcher.add_handler(CommandHandler("pin", pin))
dispatcher.add_handler(CommandHandler("purge", purge))
