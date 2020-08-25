import importlib
from random import choice

from emoji import emojize
from mongoengine import connect
from telegram import Update, BotCommand
from telegram.ext import CallbackContext, CommandHandler, run_async

from telebot import updater, config, log, dispatcher
from telebot.modules import ALL_MODULES

# Import all modules
imported_mods = {}
for module_name in ALL_MODULES:
    # check whether module is to be loaded or not
    if (config.LOAD and module_name not in config.LOAD) or (config.NO_LOAD and module_name in config.NO_LOAD):
        continue

    imported_module = importlib.import_module("telebot.modules." + module_name)

    # add imported module to the dict of modules, to be used later
    key = imported_module.__mod_name__ if imported_module.__mod_name__ else imported_module.__name__
    imported_mods[key] = imported_module

# log all imported modules
print("Imported modules :", sorted(imported_mods.keys()))


# default reply strings

START_TEXT = emojize(
    f"""
Hello, everynyan! :cat:

I'm `{updater.bot.first_name}`, a cute little bot that does rendum shit rn.
""",
    use_aliases=True,
)

HELP_TEXT = (
    START_TEXT
    + """
Use following commands to use me (*blush*):

- /help `[<modules list>]` : Recursion ftw
- /start : Turn me on
- /talk `[<word>]` : Make me meow... if you tell me what to meow then I'll do that too
- /modules : Let me tell you what all I can do to please you
"""
)


@run_async
def start(update: Update, context: CallbackContext) -> None:
    """
    Reply with the start message on running /start
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    log(update, func_name="start")
    update.message.reply_markdown(START_TEXT)


@run_async
def list_modules(update: Update, context: CallbackContext) -> None:
    """
    Reply with all the imported modules
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    log(update, "list modules")
    update.effective_message.reply_markdown(
        "The list of Active Modules is as follows :\n\n`" + "`\n`".join(imported_mods.keys()) + "`"
    )


@run_async
def help(update: Update, context: CallbackContext) -> None:
    """
    Reply with help message for the specified modules
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    log(update, func_name="help")

    text_blob = HELP_TEXT
    # add help strings of all imported modules too
    for mod_name, mod in imported_mods.items():
        if mod.__help__:
            if context.args and mod_name.lower() in map(lambda x: x.lower(), context.args):
                text_blob += f"\n`{mod_name}`\n{mod.__help__}"

    # Add informational footer
    text_blob += (
        "\n\nAll arguments that are mentioned as list are just space separated words.\n\n"
        "If you want to see help for just some select modules, "
        "run /help followed by the module names, space separated."
    )

    update.message.reply_markdown(text_blob)


@run_async
def talk(update: Update, context: CallbackContext) -> None:
    """
    Repeat a given word random number of times
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    log(update, func_name="talk")

    # get word (meow if not given)
    word = "meow "
    if context.args:
        word = context.args[0] + " "

    # make spem
    spem = (word * choice(range(100))).rstrip()
    if word != "meow ":
        spem += "\n\nmeow"

    update.message.reply_markdown(f"`{spem}`")


# set bot commands
COMMANDS = [
    BotCommand(command='talk', description="[<word>] : Say <word> (or meow, if not given) rendum number of times"),
    BotCommand(command='modules', description="List all the active modules"),
    BotCommand(command='help', description="[<module>] : Display the help text to understand how to use this bot"),
    BotCommand(command='kang', description="<reply> [<emoji>] : reply to a sticker to add it to your pack"),
]

if __name__ == "__main__":
    # create handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("talk", talk))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("modules", list_modules))

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
