import importlib
from random import choice

from telegram import Update, BotCommand
from telegram.ext import CommandHandler, CallbackContext

from telebot import dispatcher, updater, config, log
from telebot.modules import ALL_MODULES

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


# Import all modules
IMPORTED = set()
for module_name in ALL_MODULES:
    if (config.LOAD and module_name not in config.LOAD) or (config.NO_LOAD and module_name in config.NO_LOAD):
        continue

    imported_module = importlib.import_module("telebot.modules." + module_name)
    IMPORTED.add(module_name)

print("Imported modules :", sorted(IMPORTED))


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


# create handlers
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
    if config.WEBHOOK_URL:
        updater.start_webhook(listen="0.0.0.0", port=config.PORT, url_path=config.TOKEN)
        updater.bot.set_webhook(url=config.WEBHOOK_URL + config.TOKEN)

    else:
        updater.start_polling()

    print("neko chan go nyan nyan")
    updater.idle()
