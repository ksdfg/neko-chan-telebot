from os import environ

from telegram import Update
from telegram.ext import Updater


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
