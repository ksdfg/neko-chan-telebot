from telegram.ext import CommandHandler

from telebot import dispatcher, updater


def start(update, context):
    start_text = """Hello, everynyan!
    
I'm `kawai neko chan`, a cute little bot that does nothing rn.
"""
    update.message.reply_markdown(start_text)


START_COMMAND_HANDLER = CommandHandler("start", start)


if __name__ == "__main__":
    dispatcher.add_handler(START_COMMAND_HANDLER)

    updater.start_polling()
    updater.idle()
