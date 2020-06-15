from telegram import Update
from telegram.ext import run_async, CallbackContext, CommandHandler
from telegram.utils.helpers import escape_markdown

from telebot import dispatcher


@run_async
def sticker_id(update: Update, context: CallbackContext):
    rep_msg = update.effective_message.reply_to_message
    if rep_msg and rep_msg.sticker:
        update.effective_message.reply_markdown("Sticker ID:\n```" + escape_markdown(rep_msg.sticker.file_id) + "```",)
    else:
        update.effective_message.reply_text("Please reply to a sticker to get its ID.")


__help__ = """
- /stickerid: reply to a sticker to me to tell you its file ID.
"""

__mod_name__ = "Stickers"

dispatcher.add_handler(CommandHandler("stickerid", sticker_id))
