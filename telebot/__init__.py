from os import environ


# class for configuration of a bot
class Config:
    def __init__(self, token, db_uri):
        """
        Function to initialize the config for a bot
        :param token: API Token of the bot
        """

        self.TOKEN = token
        self.DB_URI = db_uri


try:
    config = Config(token=environ['TOKEN'], db_uri=environ['DATABASE_URL'])
except KeyError:
    print("Please set all required environment variables")
    exit(1)
