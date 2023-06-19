from pydantic import HttpUrl, BaseSettings
from telegram.ext import Application


# class for configuration of a bot
class Config(BaseSettings):
    ADMIN: int
    TOKEN: str

    DATABASE_NAME: str
    DATABASE_URL: str

    GITHUB_TOKEN: str

    WEBHOOK_URL: HttpUrl | None
    PORT: int = 80

    LOAD: list = []
    NO_LOAD: list = []

    PREVIEW_COMMANDS: list = []

    SUPERUSERS: list[int] = []

    class Config:
        env_file = ".env"


# create config object
config = Config()

# create updater and application
application = Application.builder().token(config.TOKEN).build()
