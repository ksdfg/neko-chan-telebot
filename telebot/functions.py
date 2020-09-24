from collections import Callable
from datetime import datetime
from functools import wraps
from traceback import print_exc, format_exc

from telegram import Update
from telegram.ext import CallbackContext
from telegram.utils.helpers import mention_markdown

from telebot import config
from telebot.modules.db.users import add_user


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
                return

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


def bot_action(func_name: str = None, extra_text: str = ""):
    """
    Function to log bot activity and execute bot_action
    :param func_name: name of the function being called
    :param extra_text: any extra text to be logged
    :return: None
    """

    def wrapper(func: Callable):
        """
        a wrapper that will safely execute the bot_action after logging it if needed
        :param func: function to execute for given bot_action
        :return: wrapper function
        """

        @wraps(func)
        def inner(update: Update, context: CallbackContext, *args, **kwargs):
            """
            log and execute the function
            :param update: object representing the incoming update.
            :param context: object containing data about the bot_action call.
            :param args: anything extra
            :param kwargs: anything extra
            :return: inner function to execute
            """
            try:
                add_user(user_id=update.effective_user.id, username=update.effective_user.username)
            except:
                print_exc()

            if func_name:
                log(update, func_name, extra_text)

            try:
                return func(update, context, *args, **kwargs)
            except:
                print_exc()
                update.effective_message.reply_markdown(
                    f"```{format_exc()}```\n\n"
                    f"Show this to {mention_markdown(user_id=config.ADMIN, name='my master')} and bribe him with some "
                    f"catnip to fix it for you..."
                )

        return inner

    return wrapper
