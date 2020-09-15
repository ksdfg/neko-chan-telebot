from telegram import Update, Message
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

    if not update.effective_message.reply_to_message:
        update.effective_message.reply_text("I'm a cat, not a psychic! Reply to the message you want to pin")
        return

    context.bot.pin_chat_message(update.effective_chat.id, update.effective_message.reply_to_message.message_id)


__mod_name__ = "Chat-Actions"

__help__ = """
- /purge `<reply>` : delete all messages from replied message to current one.
- /pin `<reply>` : pin replied message in the chat.
"""

# create handlers
dispatcher.add_handler(CommandHandler("pin", pin))
