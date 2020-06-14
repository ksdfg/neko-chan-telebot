from collections import OrderedDict
from random import choice

from telegram import Update, BotCommand
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


def log(update: Update, func_name: str, extra_text: str = ""):
    """
    Function to log bot activity
    :param username: username of the user who called a command
    :param func_name: name of the function being called
    :param extra_text: any extra text to be logged
    :return: None
    """
    print("------------------------------------")
    print(update.message.from_user.username, "called function", func_name)
    if extra_text:
        print(extra_text)


def start(update: Update, context: CallbackContext):
    # start message
    log(update, func_name="start")
    update.message.reply_markdown(START_TEXT)


def help(update: Update, context: CallbackContext):
    # display help message
    log(update, func_name="help")
    update.message.reply_markdown(HELP_TEXT)


def talk(update: Update, context: CallbackContext):
    # this cat meows
    log(update, func_name="talk")
    update.message.reply_markdown(f"`{('meow ' * choice(range(100))).rstrip()}`")


START_COMMAND_HANDLER = CommandHandler("start", start)
TALK_COMMAND_HANDLER = CommandHandler("talk", talk)
HELP_COMMAND_HANDLER = CommandHandler("help", help)


# bot commands
COMMANDS = [
    BotCommand(command='help', description="Display the help text to understand how to use this bot"),
    BotCommand(command='talk', description="This cat can meow"),
]

if __name__ == "__main__":
    # add handlers
    dispatcher.add_handler(START_COMMAND_HANDLER)
    dispatcher.add_handler(TALK_COMMAND_HANDLER)
    dispatcher.add_handler(HELP_COMMAND_HANDLER)

    # set bot commands
    updater.bot.set_my_commands(COMMANDS)

    # start bot
    updater.start_polling()

    print("neko chan can meow now")
    updater.idle()
