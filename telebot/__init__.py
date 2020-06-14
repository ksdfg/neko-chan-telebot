from os import environ


# class for configuration of a bot
class Config:
    def __init__(self, token):
        """
        Function to initialize the config for a bot
        :param token: API Token of the bot
        """

        self.TOKEN = token


try:
    config = Config(token=environ['TOKEN'])
except KeyError:
    print("Please set all required environment variables")
    exit(1)
