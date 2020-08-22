from decouple import config
from telegram import Update
from telegram.ext import Updater


# class for configuration of a bot
class Config:
    def __init__(self, token, db_name, db_uri, webhook_url=False, port=False, load=None, no_load=None):
        """
        Function to initialize the config for a bot
        :param token: Your bot token, as a string.
        :param db_uri: Your database URL
        :param webhook_url: The URL your webhook should connect to (only needed for webhook mode)
        :param port: Port to use for your webhooks
        """

        self.TOKEN = token
        self.DB_NAME = db_name
        self.DB_URI = db_uri
        self.WEBHOOK_URL = webhook_url
        self.PORT = port

        self.LOAD = load
        self.NO_LOAD = no_load


def log(update: Update, func_name: str, extra_text: str = ""):
    """
    Function to log bot activity
    :param update: Update object to retrieve info from
    :param func_name: name of the function being called
    :param extra_text: any extra text to be logged
    :return: None
    """
    chat = "private chat"
    if update.effective_chat.type != "private":
        chat = update.effective_chat.title

    print(update.effective_user.username, "called function", func_name, "from", chat)
    if extra_text:
        print(extra_text)


# create config object
config = Config(
    token=config('TOKEN'),
    db_name=config('DATABASE_NAME'),
    db_uri=config('DATABASE_URL', default=None),
    webhook_url=config('WEBHOOK_URL', default=False),
    port=config('PORT', default=False),
    load=config('LOAD', default=False, cast=lambda x: x.split(" ") if x else False),
    no_load=config('NO_LOAD', default=False, cast=lambda x: x.split(" ") if x else False),
)

# create updater and dispatcher
updater = Updater(config.TOKEN, use_context=True)
dispatcher = updater.dispatcher
