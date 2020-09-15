from random import choice

from emoji import emojize
from telegram import Update, User
from telegram.ext import CallbackContext, CommandHandler, run_async
from telegram.utils.helpers import escape_markdown, mention_markdown

from telebot import updater, dispatcher
from telebot.modules import imported_mods
from telebot.functions import log

# default Start Text
START_TEXT = emojize(
    f"""
NyaHello World! :cat:

I'm `{updater.bot.first_name}`, a cute little bot that does rendum shit rn.
""",
    use_aliases=True,
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
        "The list of Active Modules is as follows :\n\n`"
        + "`\n`".join(mod.__mod_name__ for mod in imported_mods.values())
        + "`"
    )


@run_async
def help(update: Update, context: CallbackContext) -> None:
    """
    Reply with help message for the specified modules
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    log(update, func_name="help")

    text_blob = START_TEXT + "\n_Use following commands to use me_ (*blush*):\n"

    if not context.args:
        # meme descriptions of basic commands
        text_blob += """
- /help `[<modules list>]` : Recursion ftw

- /start : Turn me on

- /talk `[<word>]` : Make me meow... if you tell me what to meow then I'll do that too

- /modules : Let me tell you what all I can do to please you
        """
    else:
        # add help strings of all imported modules too
        for module in context.args:
            try:
                mod = imported_mods[module.lower()]
                text_blob += f"\n`{mod.__mod_name__}`\n{mod.__help__}"
            except KeyError:
                continue

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


@run_async
def get_id(update: Update, context: CallbackContext) -> None:
    """
    Function to get chat and user ID
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    log(update, "id")

    update.effective_message.reply_markdown(
        f"Your ID is :\n`{update.effective_user.id}`\n\nThe chat ID is :\n`{update.effective_chat.id}`"
    )


def info(update: Update, context: CallbackContext):
    """
    Function to get user details
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    log(update, "info")

    # get user to display info of
    user: User = update.message.reply_to_message.from_user if update.message.reply_to_message else update.effective_user

    # make info string
    reply = f"*ID* : `{user.id}`\n"
    if user.first_name:
        reply += f"*First Name* : `{user.first_name}`\n"
    if user.last_name:
        reply += f"*Last Name* : `{user.last_name}`\n"
    if user.username:
        reply += f"*Username* : @{escape_markdown(user.username)}\n\n"
    reply += mention_markdown(user_id=user.id, name="Click here to properly check out this kitten")

    # send user info
    update.effective_message.reply_markdown(reply)


__mod_name__ = "Basics"

__help__ = """
- /help `[<modules list>]` : Display the help text to understand how to use this bot

- /start : Start the bot! Gives a small welcome message

- /talk `[<word>]` : Say <word> (or meow, if not given) rendum number of times

- /modules : List all the active modules

- /id : Get the user and chat ID

- /info `[<reply>]` : Get details of a user (by replying to their message) or yourself
"""


# create handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("talk", talk))
dispatcher.add_handler(CommandHandler("help", help))
dispatcher.add_handler(CommandHandler("modules", list_modules))
dispatcher.add_handler(CommandHandler("id", get_id))
dispatcher.add_handler(CommandHandler("info", info))
