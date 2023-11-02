from pydantic import HttpUrl
from telegram.ext import Updater
from pydantic_settings import BaseSettings, SettingsConfigDict


# class for configuration of a bot
class Config(BaseSettings):
    ADMIN: int
    TOKEN: str

    DATABASE_NAME: str
    DATABASE_URL: str

    GITHUB_TOKEN: str

    WEBHOOK_URL: HttpUrl | None = None
    PORT: int = 80

    LOAD: list = []
    NO_LOAD: list = []

    PREVIEW_COMMANDS: list = []

    SUPERUSERS: list[int] = []

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


# create config object
config = Config()

# create updater and dispatcher
updater = Updater(config.TOKEN, use_context=True)
dispatcher = updater.dispatcher
