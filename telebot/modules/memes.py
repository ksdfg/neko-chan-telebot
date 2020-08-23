from telegram import Update
from telegram.ext import CallbackContext, CommandHandler

from telebot import dispatcher, log


def runs(update: Update, context: CallbackContext):
    log(update, "runs")
    update.effective_message.reply_markdown("I'm a cute kitty, and here we have a fat pussy.")
    update.effective_chat.send_sticker("CAACAgUAAxkBAAIJK19CjPoyyX9QwwHfNOZMnqww1hxXAALfAAPd6BozJDBFCIENpGkbBA")


__help__ = """
"""

__mod_name__ = "memes"

dispatcher.add_handler(CommandHandler("runs", runs))
