from decouple import config
from telegram.ext import Updater


# class for configuration of a bot
class Config:
    def __init__(
        self,
        admin,
        token,
        db_name,
        db_uri,
        github_token,
        webhook_url=False,
        port=False,
        load=None,
        no_load=None,
        preview_commands=None,
        superusers=None,
    ):
        """
        Function to initialize the config for a bot
        :param admin: user ID of the bot admin
        :param token: Your bot token, as a string.
        :param db_uri: Your database URL
        :param webhook_url: The URL your webhook should connect to (only needed for webhook mode)
        :param port: Port to use for your webhooks
        """

        if superusers is None:
            superusers = []

        self.ADMIN = admin
        self.TOKEN = token

        self.DB_NAME = db_name
        self.DB_URI = db_uri

        self.GITHUB_TOKEN = github_token

        self.WEBHOOK_URL = webhook_url
        self.PORT = port

        self.LOAD = load
        self.NO_LOAD = no_load
        self.PREVIEW_COMMANDS = preview_commands

        self.SUPERUSERS = superusers


# create config object
config = Config(
    admin=config("ADMIN", cast=int),
    token=config("TOKEN"),
    db_name=config("DATABASE_NAME"),
    db_uri=config("DATABASE_URL", default=None),
    github_token=config("GITHUB_TOKEN"),
    webhook_url=config("WEBHOOK_URL", default=False),
    port=config("PORT", default=80, cast=int),
    load=config("LOAD", default=False, cast=lambda x: x.split(" ") if x else False),
    no_load=config("NO_LOAD", default=False, cast=lambda x: x.split(" ") if x else False),
    preview_commands=config("PREVIEW_COMMANDS", default=[], cast=lambda x: x.split(" ") if x else []),
    superusers=config("SUPERUSERS", default=[], cast=lambda x: map(int, x.split(" "))),
)

# create updater and dispatcher
updater = Updater(config.TOKEN, use_context=True)
dispatcher = updater.dispatcher
