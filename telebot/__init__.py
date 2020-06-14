from os import environ

from telegram.ext import Updater


# class for configuration of a bot
class Config:
    def __init__(self, token, db_uri, webhook_url=False, port=False):
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


# create config object
config = Config(
    token=environ['TOKEN'],
    db_uri=environ['DATABASE_URL'],
    webhook_url=environ.get('WEBHOOK_URL', False),
    port=environ.get('PORT', False),
)

# create updater and dispatcher
updater = Updater(config.TOKEN, use_context=True)
dispatcher = updater.dispatcher
