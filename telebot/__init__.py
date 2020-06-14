from os import environ
from random import choice

from telegram import Update, BotCommand
from telegram.ext import Updater, CallbackContext, CommandHandler


# class for configuration of a bot
class Config:
    def __init__(self, token, db_uri, webhook_url=False, port=False, load=None, no_load=None):
        """
        Function to initialize the config for a bot
        :param token: Your bot token, as a string.
        :param db_uri: Your database URL
        :param webhook_url: The URL your webhook should connect to (only needed for webhook mode)
        :param port: Port to use for your webhooks
        """

        self.TOKEN = token
        self.DB_URI = db_uri
        self.WEBHOOK_URL = webhook_url
        self.PORT = port

        self.LOAD = load.split(" ") if load else False
        self.NO_LOAD = no_load.split(" ") if no_load else False


def log(update: Update, func_name: str, extra_text: str = ""):
    """
    Function to log bot activity
    :param update: Update object to retrieve info from
    :param func_name: name of the function being called
    :param extra_text: any extra text to be logged
    :return: None
    """
    print("------------------------------------")
    print(update.effective_user.username, "called function", func_name)
    if extra_text:
        print(extra_text)


# create config object
config = Config(
    token=environ['TOKEN'],
    db_uri=environ['DATABASE_URL'],
    webhook_url=environ.get('WEBHOOK_URL', False),
    port=environ.get('PORT', False),
    load=environ.get('LOAD', False),
    no_load=environ.get('NO_LOAD', False),
)

# create updater and dispatcher
updater = Updater(config.TOKEN, use_context=True)
dispatcher = updater.dispatcher


# default reply strings

START_TEXT = """
Hello, everynyan!

I'm `kawai neko chan`, a cute little bot that does rendum shit rn.
"""

HELP_TEXT = """
Hello, everynyan!

I'm `kawai neko chan`, a cute little bot that does rendum shit rn.

Use following commands to use me (*blush*):
/help - Recursion ftw
/start - Turn me on
/talk - Make me meow
"""


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

    word = "meow "
    if context.args:
        word = context.args[0] + " "

    update.message.reply_markdown(f"`{(word * choice(range(100))).rstrip()}`")
    if word != "meow ":
        update.message.reply_markdown(f"`meow`")


# create handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("talk", talk))
dispatcher.add_handler(CommandHandler("help", help))


# set bot commands
COMMANDS = [
    BotCommand(command='help', description="Display the help text to understand how to use this bot"),
    BotCommand(command='talk', description="Say <word> (or meow, if not given) rendum number of times."),
]

updater.bot.set_my_commands(COMMANDS)
