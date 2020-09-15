from mongoengine import connect
from telegram import BotCommand

from telebot import updater, config
from telebot.modules import imported_mods

# log all imported modules
print("Imported modules :", sorted(mod.__mod_name__ for mod in imported_mods.values()))

# set bot commands
COMMANDS = [
    BotCommand(command='talk', description="[<word>] : Say <word> (or meow, if not given) rendum number of times"),
    BotCommand(command='modules', description="List all the active modules"),
    BotCommand(
        command='help', description="[<modules list>] : Display the help text to understand how to use this bot"
    ),
    BotCommand(command='kang', description="<reply> [<emoji>] : Reply to a sticker to add it to your pack"),
    BotCommand(command='id', description="Get the user and chat ID"),
]

if __name__ == "__main__":
    updater.bot.set_my_commands(COMMANDS)  # set bot commands to be displayed

    # connect to database
    connect(config.DB_NAME, 'default', host=config.DB_URI)

    # start bot
    if config.WEBHOOK_URL:
        updater.start_webhook(listen="0.0.0.0", port=config.PORT, url_path=config.TOKEN)
        updater.bot.set_webhook(url=config.WEBHOOK_URL + config.TOKEN)
    else:
        updater.start_polling()

    print("neko chan go nyan nyan")
    updater.idle()
