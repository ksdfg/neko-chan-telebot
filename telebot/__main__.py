from mongoengine import connect
from telegram import BotCommand

from telebot import updater, config
from telebot.modules import imported_mods

# log all imported modules
print("Imported modules :", ", ".join(sorted(mod.__mod_name__ for mod in imported_mods.values())))

# set bot commands
COMMANDS = []

# add commands from basics
if "Basics" in [mod.__mod_name__ for mod in imported_mods.values()]:
    COMMANDS += [
        BotCommand(command='talk', description="[<word>] : Say <word> (or meow, if not given) rendum number of times"),
        BotCommand(command='modules', description="List all the active modules"),
        BotCommand(
            command='help', description="[<modules list>] : Display the help text to understand how to use this bot"
        ),
        BotCommand(command='id', description="[<reply|username>] : Get details of chat and a user or yourself"),
    ]

# add commands from stickers
if "Stickers" in [mod.__mod_name__ for mod in imported_mods.values()]:
    COMMANDS.append(
        BotCommand(command='kang', description="<reply> [<emoji>] : Reply to a sticker to add it to your pack")
    )

# add commands from delete
if "Delete" in [mod.__mod_name__ for mod in imported_mods.values()]:
    COMMANDS.append(BotCommand(command='del', description="<reply> : delete the quoted message."))

if __name__ == "__main__":
    updater.bot.set_my_commands(COMMANDS)  # set bot commands to be displayed

    # connect to database
    connect(config.DB_NAME, 'default', host=config.DB_URI)

    # start bot
    if config.WEBHOOK_URL:
        updater.bot.delete_webhook()  # in case there's one up
        updater.start_webhook(
            listen="0.0.0.0", port=config.PORT, url_path=config.TOKEN, webhook_url=config.WEBHOOK_URL + config.TOKEN
        )
    else:
        updater.start_polling()

    print("neko chan go nyan nyan")
    updater.idle()
