from os import environ

from telegram.ext import Updater


# class for configuration of a bot
class Config:
    def __init__(self, token, db_uri):
        """
        Function to initialize the config for a bot
        :param token: API Token of the bot
        """

        self.TOKEN = token
        self.DB_URI = db_uri


# create config object
config = Config(token=environ['TOKEN'], db_uri=environ['DATABASE_URL'])

# create updater and dispatcher
updater = Updater(config.TOKEN, use_context=True)
dispatcher = updater.dispatcher
