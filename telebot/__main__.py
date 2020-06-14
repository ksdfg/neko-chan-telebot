from collections import OrderedDict
from random import choice

from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

from telebot import dispatcher, updater, config

# default reply strings

START_TEXT = """
Hello, everynyan!

I'm `kawai neko chan`, a cute little bot that does rendum shit rn.
"""

HELP_TEXT = """
Hello, everynyan!

I'm `kawai neko chan`, a cute little bot that does rendum shit rn.

Use following commands to use me (*blush*):
/help - recursion ftw
/start - turn me on
/talk - make me meow
"""


def log(username: str, func_name: str, extra_text: str = ""):
    """
    Function to log bot activity
    :param username: username of the user who called a command
    :param func_name: name of the function being called
    :param extra_text: any extra text to be logged
    :return: None
    """
    print("------------------------------------")
    print(username, "called function", func_name)
    if extra_text:
        print(extra_text)


def start(update: Update, context: CallbackContext):
    # start message
    log(username=update.message.from_user.username, func_name="start")
    update.message.reply_markdown(START_TEXT)


def help(update: Update, context: CallbackContext):
    # display help message
    log(username=update.message.from_user.username, func_name="help")
    update.message.reply_markdown(HELP_TEXT)


def talk(update: Update, context: CallbackContext):
    # this cat meows
    log(username=update.message.from_user.username, func_name="talk")
    update.message.reply_markdown(f"`{('meow ' * choice(range(100))).rstrip()}`")


START_COMMAND_HANDLER = CommandHandler("start", start)
TALK_COMMAND_HANDLER = CommandHandler("talk", talk)
HELP_COMMAND_HANDLER = CommandHandler("help", help)


if __name__ == "__main__":
    # add handlers
    dispatcher.add_handler(START_COMMAND_HANDLER)
    dispatcher.add_handler(TALK_COMMAND_HANDLER)
    dispatcher.add_handler(HELP_COMMAND_HANDLER)

    # start bot
    updater.start_polling()

    print("neko chan can meow now")
    updater.idle()
