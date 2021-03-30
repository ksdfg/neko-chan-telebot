from random import choice

from emoji import emojize
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler
from telegram.utils.helpers import escape_markdown

from telebot import updater, dispatcher
from telebot.utils import bot_action, get_user_from_message, UserError, UserRecordError
from telebot.modules import imported_mods

# default Start Text

START_TEXT = emojize(
    f"""
NyaHello World! :cat:

I'm `{updater.bot.first_name}`, a cute little bot that does rendum shit rn.
""",
    use_aliases=True,
)


@bot_action("start")
def start(update: Update, context: CallbackContext):
    """
    Reply with the start message on running /start
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    update.message.reply_markdown(START_TEXT)


@bot_action("list modules")
def list_modules(update: Update, context: CallbackContext):
    """
    Reply with all the imported modules
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    update.effective_message.reply_markdown(
        "The list of Active Modules is as follows :\n\n`"
        + "`\n`".join(mod.__mod_name__.title() for mod in imported_mods.values())
        + "`"
    )


@bot_action("help")
def help(update: Update, context: CallbackContext):
    """
    Reply with help message for the specified modules
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
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


@bot_action("talk")
def talk(update: Update, context: CallbackContext) -> None:
    """
    Repeat a given word random number of times
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    # get word (meow if not given)
    word = "meow "
    if context.args:
        word = context.args[0] + " "

    # make spem
    spem = (word * choice(range(100))).rstrip()
    if word != "meow ":
        spem += "\n\nmeow"

    update.message.reply_markdown(f"`{spem}`")


@bot_action("file id")
def get_file_id(update: Update, context: CallbackContext) -> None:
    """
    Function to get chat and user ID
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    msg = update.effective_message.reply_to_message
    if msg.audio:
        file = msg.audio
    elif msg.video:
        file = msg.video
    elif msg.sticker:
        file = msg.sticker
    elif msg.photo:
        file = msg.photo
    elif msg.voice:
        file = msg.voice
    else:
        update.effective_message.reply_text("Find the cat that can find your file, cuz this cat can't.")
        return

    update.effective_message.reply_markdown(f"`{file.file_id}`")


@bot_action("id")
def info(update: Update, context: CallbackContext):
    """
    Function to get user details
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    # get user to display info of
    try:
        user_id, _ = get_user_from_message(update.effective_message)
        user = update.effective_chat.get_member(user_id).user
    except UserError:
        user = update.effective_user
    except UserRecordError as e:
        update.effective_message.reply_text(e.message)
        return

    # make info string
    reply = f"*Chat ID*: `{update.effective_chat.id}`\n\n*ID*: `{user.id}`\n"
    if first_name := user.first_name:
        reply += f"*First Name*: `{first_name}`\n"
    if last_name := user.last_name:
        reply += f"*Last Name*: `{last_name}`\n"
    if username := user.username:
        reply += f"*Username*: @{escape_markdown(username)}\n\n"
    reply += user.mention_markdown(name="Click here to properly check this kitten out")

    # send user info
    update.effective_message.reply_markdown(reply)


__mod_name__ = "Basics"

__help__ = """
- /help `[<modules list>]` : Display the help text to understand how to use this bot

- /start : Start the bot! Gives a small welcome message

- /talk `[<word>]` : Say <word> (or meow, if not given) rendum number of times

- /modules : List all the active modules

- /id `[<reply|username>]` : Get details of current chat and a user (by replying to their message or giving their username) or yourself

- /fileid `<reply>` : Get file ID of the file in the quoted message
"""


# create handlers
dispatcher.add_handler(CommandHandler("start", start, run_async=True))
dispatcher.add_handler(CommandHandler("talk", talk, run_async=True))
dispatcher.add_handler(CommandHandler("help", help, run_async=True))
dispatcher.add_handler(CommandHandler("modules", list_modules, run_async=True))
dispatcher.add_handler(CommandHandler("id", info, run_async=True))
dispatcher.add_handler(CommandHandler("fileid", get_file_id, run_async=True))
