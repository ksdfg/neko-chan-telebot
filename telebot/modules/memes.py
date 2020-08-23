from spongemock.spongemock import mock as mock_text
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, run_async

from telebot import dispatcher, log


@run_async
def runs(update: Update, context: CallbackContext):
    log(update, "runs")
    update.effective_message.reply_markdown("I'm a cute kitty, and here we have a fat pussy.")
    update.effective_chat.send_sticker("CAACAgUAAxkBAAIJK19CjPoyyX9QwwHfNOZMnqww1hxXAALfAAPd6BozJDBFCIENpGkbBA")


@run_async
def mock(update: Update, context: CallbackContext):
    log(update, "mock")

    if update.effective_message.reply_to_message:
        update.effective_message.reply_to_message.reply_text(mock_text(update.effective_message.reply_to_message.text))
    else:
        update.effective_message.reply_text("I don't see anything to mock here other than your ugly face...")


__help__ = """
/mock : MoCk LikE sPOnGEbob
"""

__mod_name__ = "memes"

dispatcher.add_handler(CommandHandler("runs", runs))
dispatcher.add_handler(CommandHandler("mock", mock))
