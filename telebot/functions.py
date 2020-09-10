from collections import Callable
from functools import wraps

from telegram import Update
from telegram.ext import CallbackContext

# Some Helper Functions


def check_user_admin(func: Callable):
    """
    Wrapper function for checking if user is admin
    :param func: The function this wraps over
    """

    @wraps(func)
    def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        if update.effective_chat.type != "private":
            # check if user is admin
            if update.effective_chat.get_member(update.effective_user.id).status not in ('administrator', 'creator'):
                update.effective_message.reply_text(
                    "Get some admin privileges before you try to order me around, baka!"
                )
            else:
                func(update, context, *args, **kwargs)

    return wrapper


def check_bot_admin(func: Callable):
    """
    Wrapper function for checking if bot is admin
    :param func: The function this wraps over
    """

    @wraps(func)
    def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        if update.effective_chat.type != "private":
            # check if bot is an admin
            if update.effective_chat.get_member(context.bot.id).status not in ('administrator', 'creator'):
                update.effective_message.reply_text("Ask your sugar daddy to give me admin status plej...")
                return
            else:
                func(update, context, *args, **kwargs)

    return wrapper


def log(update: Update, func_name: str, extra_text: str = ""):
    """
    Function to log bot activity
    :param update: Update object to retrieve info from
    :param func_name: name of the function being called
    :param extra_text: any extra text to be logged
    :return: None
    """
    chat = "private chat"
    if update.effective_chat.type != "private":
        chat = update.effective_chat.title

    print(update.effective_user.username, "called function", func_name, "from", chat)
    if extra_text:
        print(extra_text)
