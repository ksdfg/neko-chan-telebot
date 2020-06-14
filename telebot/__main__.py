from collections import OrderedDict
from random import choice

from telegram.ext import CommandHandler

from telebot import dispatcher, updater


START_TEXT = """
Hello, everynyan!

I'm `kawai neko chan`, a cute little bot that does nothing rn.
"""


def start(update, context):
    # start message
    print(update.message.from_user.username, "called start function")
    update.message.reply_markdown(START_TEXT)


def talk(update, context):
    # this cat meows
    print(update.message.from_user.username, "called talk function")
    update.message.reply_markdown(f"`{('meow ' * choice(range(100))).rstrip()}`")


START_COMMAND_HANDLER = CommandHandler("start", start)
TALK_COMMAND_HANDLER = CommandHandler("talk", talk)


if __name__ == "__main__":
    # add handlers
    dispatcher.add_handler(START_COMMAND_HANDLER)
    dispatcher.add_handler(TALK_COMMAND_HANDLER)

    updater.start_polling()
    print("neko chan can meow now")
    updater.idle()
