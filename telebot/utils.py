import time
from functools import wraps
from http import HTTPStatus
from traceback import print_exc, format_exc
from typing import Callable, Tuple

from emoji import emojize
from requests import post
from telegram import Update, Message, MessageEntity
from telegram.error import BadRequest
from telegram.ext import CallbackContext
from telegram.utils.helpers import mention_markdown

from telebot import config
from telebot.modules.db.chat_commands import check_command_for_chat
from telebot.modules.db.users import add_user, get_user


# Class to represent all the info required to describe how to use a command
class CommandDescription:
    def __init__(
        self,
        command: str,
        description: str,
        args: str = "",
        is_admin: bool = False,
        is_slash_command: bool = True,
    ):
        self.command = command
        self.args = args
        self.description = description
        self.is_admin = is_admin
        self.is_slash_command = is_slash_command

    def help_text(self) -> str:
        """
        :return: text to append to help command text blobs
        """
        return f"- {'/' if self.is_admin else ''}{self.command} {f'`{self.args}` ' if self.args else ''}:{' *(admin only)*' if self.is_admin else ''} {self.description}"

    def bot_command_description(self) -> str:
        """
        :return: description to set in bot command previews
        """
        return f"{f'{self.args} :' if self.args else ''}{' (admin only)' if self.is_admin else ''} {self.description.split('.')[0]}"


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
            if update.effective_chat.get_member(update.effective_user.id).status not in ("administrator", "creator"):
                update.effective_message.reply_text(
                    "Get some admin privileges before you try to order me around, baka!"
                )
                return

        return func(update, context, *args, **kwargs)

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
            if update.effective_chat.get_member(context.bot.id).status not in ("administrator", "creator"):
                update.effective_message.reply_text("Ask your sugar daddy to give me admin status plej...")
                return

        return func(update, context, *args, **kwargs)

    return wrapper


def check_reply_to_message(error_msg: str):
    """
    Check if the message has a reply_to_message
    :param error_msg: message to send when there is no reply_to_message
    :return: wrapper
    """

    def wrapper(func: Callable):
        """
        a wrapper that will safely execute the function after checking if it has a reply_to
        :param func: function to execute after check
        :return: wrapper function
        """

        @wraps(func)
        def inner(update: Update, context: CallbackContext, *args, **kwargs):
            """
            check and execute the function
            :param update: object representing the incoming update.
            :param context: object containing data about the bot_action call.
            :param args: anything extra
            :param kwargs: anything extra
            :return: inner function to execute
            """
            if update.effective_message.reply_to_message:
                # store user info for future usage
                try:
                    add_user(
                        user_id=update.effective_message.reply_to_message.from_user.id,
                        username=update.effective_message.reply_to_message.from_user.username,
                    )
                except:
                    print_exc()

                return func(update, context, *args, **kwargs)  # execute the function

            else:
                update.effective_message.reply_markdown(error_msg)

        return inner

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


def create_gist(err: str) -> str:
    """
    Function to create gists with errors
    :param err: error to set in gist
    :return: url to the created gis
    """
    headers = {"Accept": "application/vnd.github.v3+json", "Authorization": f"token {config.GITHUB_TOKEN}"}
    body = {"description": "error from neko chan", "files": {f"neko-chan-errors-{time.time()}": {"content": err}}}

    response = post("https://api.github.com/gists", headers=headers, json=body)
    if response.status_code != HTTPStatus.CREATED:
        raise Exception(f"invalid status code from gist: {response.status_code}")

    return response.json().get("html_url")


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
            except BadRequest as e:
                if e.message == "Message is too long":
                    update.effective_message.reply_text(
                        emojize(
                            "I tried to send a message so long that my tongue got tired :sad_but_relieved_face: "
                            "This is not gonna work, let's try something else..."
                        )
                    )
                else:
                    print_exc()
                    try:
                        err = create_gist(format_exc())
                    except:
                        err = f"```{format_exc()}```"

                    update.effective_message.reply_markdown(
                        f"{err}\n\n"
                        f"Show this to {mention_markdown(user_id=config.ADMIN, name='my master')} and bribe him with "
                        "some catnip to fix it for you..."
                    )
            except:
                print_exc()
                try:
                    err = create_gist(format_exc())
                except:
                    err = f"```{format_exc()}```"

                update.effective_message.reply_markdown(
                    f"{err}\n\n"
                    f"Show this to {mention_markdown(user_id=config.ADMIN, name='my master')} and bribe him with "
                    "some catnip to fix it for you..."
                )

        return inner

    return wrapper


def check_command(command: str = None):
    """
    Check if a given command is enabled for chat
    :param command: name of the command being called
    :return: None
    """

    def wrapper(func: Callable):
        """
        a wrapper that will safely execute the command after checking if it is enabled
        :param func: function to execute for given bot_action
        :return: wrapper function
        """

        @wraps(func)
        def inner(update: Update, context: CallbackContext, *args, **kwargs):
            """
            check command and execute the function
            :param update: object representing the incoming update.
            :param context: object containing data about the bot_action call.
            :param args: anything extra
            :param kwargs: anything extra
            :return: inner function to execute
            """
            if not check_command_for_chat(update.effective_chat.id, command):
                update.effective_message.reply_text(
                    "This command is forbidden in this chat! If you want to do forbidden stuff, go to Alabama..."
                )
                return

            return func(update, context, *args, **kwargs)

        return inner

    return wrapper


# exception class for when no user is found for given message
class UserError(Exception):
    pass


# exception class for when no user is found in the DB
class UserRecordError(Exception):
    def __init__(self):
        self.message = (
            "I don't remember anyone with that username... "
            "Maybe try executing the same command, but reply to a message by this user instead?"
        )
        super(UserRecordError, self).__init__(self.message)


def get_user_from_message(message: Message) -> Tuple[int, str]:
    """
    Get the User ID of a user from a given message from either the reply to message, or username given in content
    :param message: The message whose content or reply to message we need to check
    :return: User ID of the user
    """
    if message.reply_to_message:
        # get user who made the quoted message
        user_id = message.reply_to_message.from_user.id
        username = message.reply_to_message.from_user.username
        add_user(user_id=user_id, username=username)  # for future usage

    elif len(message.text.split(" ")) > 1:
        # get user from our users database using his username
        usernames = list(message.parse_entities([MessageEntity.MENTION]).values())
        if usernames:
            user_id = get_user(username=usernames[0][1:])
            if not user_id:
                raise UserRecordError()
            username = usernames[0][1:]
        else:
            raise UserError()

    else:
        raise UserError()

    return user_id, username
