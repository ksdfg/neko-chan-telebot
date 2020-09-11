from decouple import config
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


# create config object
config = Config(
    token=config('TOKEN'),
    db_name=config('DATABASE_NAME'),
    db_uri=config('DATABASE_URL', default=None),
    webhook_url=config('WEBHOOK_URL', default=False),
    port=config('PORT', default=80),
    load=config('LOAD', default=False, cast=lambda x: x.split(" ") if x else False),
    no_load=config('NO_LOAD', default=False, cast=lambda x: x.split(" ") if x else False),
)

# create updater and dispatcher
updater = Updater(config.TOKEN, use_context=True)
dispatcher = updater.dispatcher
