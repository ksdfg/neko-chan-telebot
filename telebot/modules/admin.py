from datetime import datetime, timedelta
from functools import wraps
from os.path import join, dirname
from re import match
from typing import Callable, List, Optional

from emoji import emojize
from pytz import timezone
from telegram import Update, ChatPermissions, ChatMember
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler
from telegram.utils.helpers import escape_markdown, mention_markdown

from telebot import dispatcher
from telebot.modules.db.exceptions import get_command_exception_chats
from telebot.modules.db.mute import add_muted_member, remove_muted_member
from telebot.modules.db.users import add_user
from telebot.utils import (
    check_user_admin,
    check_bot_admin,
    bot_action,
    get_user_from_message,
    UserError,
    UserRecordError,
    CommandDescription,
)


def for_chat_types(*types):
    """
    Allow a command to run only in the following types of functions
    :param types: the list of types of chats to allow the command in
    :return: wrapper that does the above check
    """

    def wrapper(func: Callable):
        """
        Wrapper function for making sure chat is within the given types only
        :param func: The function this wraps over
        """

        @wraps(func)
        def inner(update: Update, context: CallbackContext, *args, **kwargs):
            if update.effective_chat.type not in types:
                update.effective_message.reply_text(f"Sorry, can't do that in a {update.effective_chat.type}...")
                return

            func(update, context, *args, **kwargs)

        return inner

    return wrapper


def can_restrict(func: Callable):
    """
    Wrapper function for checking if user and bot has perms required for muting and un-muting
    :param func: The function this wraps over
    """

    @wraps(func)
    def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        if update.effective_chat.type != "private" and update.effective_chat.id not in get_command_exception_chats(
            "admin"
        ):
            # check bot
            if not update.effective_chat.get_member(context.bot.id).can_restrict_members:
                update.effective_message.reply_markdown(
                    "Ask your sugar daddy to give me perms required to use the method `CanRestrictMembers`."
                )
                return

            # check user
            user = update.effective_chat.get_member(update.effective_user.id)
            if not user.can_restrict_members and user.status != "creator":
                update.effective_message.reply_markdown(
                    "Ask your sugar daddy to give you perms required to use the method `CanRestrictMembers`."
                )
                return

        func(update, context, *args, **kwargs)

    return wrapper


# custom exception for when user gives the time in wrong format in message
class TimeFormatException(Exception):
    pass


def get_datetime_form_args(args: List[str], username: str = "") -> Optional[datetime]:
    """
    Get the time quoted by a user from the args
    :param args: context.args
    :param username: username quoted in the message, if any
    :return:
    """

    # get all args other than the username
    useful_args = []
    for arg in args:
        if username not in arg:
            useful_args.append(arg)

    if useful_args:
        # get datetime till when we have to mute user
        time, unit = float(useful_args[0][:-1]), useful_args[0][-1]
        match unit:
            case "d":
                return datetime.now(tz=timezone("Asia/Kolkata")) + timedelta(days=time)
            case "h":
                return datetime.now(tz=timezone("Asia/Kolkata")) + timedelta(hours=time)
            case "m":
                return datetime.now(tz=timezone("Asia/Kolkata")) + timedelta(minutes=time)
            case _:
                raise TimeFormatException


@bot_action("mute")
@for_chat_types("supergroup")
@check_user_admin
@check_bot_admin
@can_restrict
def mute(update: Update, context: CallbackContext):
    """
    Mute a user, temporarily or permanently
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    # kwargs to pass to the restrict_chat_member function call
    kwargs = {"chat_id": update.effective_chat.id}

    # get user to mute
    try:
        user_id, username = get_user_from_message(update.effective_message)
        kwargs["user_id"] = user_id
    except UserError:
        update.effective_message.reply_text(
            "Reply to a message by the user or give username of user you want to mute..."
        )
        return
    except UserRecordError as e:
        update.effective_message.reply_text(e.message)
        return

    # check if user is trying to mute an admin
    user = update.effective_chat.get_member(kwargs["user_id"])
    if user.status in ("administrator", "creator"):
        update.effective_message.reply_text("I can't mute an admin, baka!")
        return

    # set muted permissions
    kwargs["permissions"] = ChatPermissions(
        can_send_messages=False,
        can_send_media_messages=False,
        can_send_other_messages=False,
        can_send_polls=False,
        can_add_web_page_previews=False,
        can_change_info=user.can_change_info,
        can_invite_users=user.can_invite_users,
        can_pin_messages=user.can_pin_messages,
    )

    # get datetime till when we have to mute user
    try:
        kwargs["until_date"] = get_datetime_form_args(context.args, username)
    except TimeFormatException:
        update.effective_message.reply_markdown(
            "Please give the unit of time as one of the following\n\n`m` = minutes\n`h` = hours\n`d` = days"
        )
        return
    except ValueError:
        update.effective_message.reply_text("Time needs to be a number, baka!")
        return

    # add muted member in db
    if add_muted_member(
        chat=kwargs["chat_id"],
        user=kwargs["user_id"],
        username=username,
        until_date=kwargs["until_date"] if "until_date" in kwargs.keys() else None,
    ):
        # mute member
        context.bot.restrict_chat_member(**kwargs)
        reply = (
            f"Sewed up @{escape_markdown(username)}'s mouth :smiling_face_with_horns:\nIf you want to be un-muted, "
            f"bribe an admin with some catnip to do it for you..."
        )
        if kwargs["until_date"]:
            reply += f" or wait till `{kwargs['until_date'].strftime('%c')} IST`"

        update.effective_message.reply_markdown(emojize(reply))
    else:
        update.effective_message.reply_text("Couldn't save record in db....")


@bot_action("un mute")
@for_chat_types("supergroup")
@check_user_admin
@check_bot_admin
@can_restrict
def unmute(update: Update, context: CallbackContext):
    """
    Unmute a muted user
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    # kwargs to pass to the restrict_chat_member function call
    kwargs = {"chat_id": update.effective_chat.id}

    # get user to un mute
    try:
        user_id, username = get_user_from_message(update.effective_message)
        kwargs["user_id"] = user_id
    except UserError:
        update.effective_message.reply_text(
            "Reply to a message by the user or give username of user you want to unmute..."
        )
        return
    except UserRecordError as e:
        update.effective_message.reply_text(e.message)
        return

    # set default permissions
    kwargs["permissions"] = context.bot.get_chat(update.effective_chat.id).permissions

    # unmute member
    if remove_muted_member(chat=kwargs["chat_id"], user=kwargs["user_id"]):
        context.bot.restrict_chat_member(**kwargs)
        update.effective_message.reply_text(f"@{username} can now go nyan nyan")
    else:
        update.effective_message.reply_text("Couldn't remove record from db....")


def ban_kick(update: Update, context: CallbackContext):
    """
    ban or kick a user from a chat
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    action = "ban" if match("^/ban.*$", update.effective_message.text) else "kick"

    # kwargs to pass to the ban_chat_member function call
    kwargs = {"chat_id": update.effective_chat.id}

    # get user to ban
    try:
        user_id, username = get_user_from_message(update.effective_message)
        kwargs["user_id"] = user_id
    except UserError:
        update.effective_message.reply_text(
            f"Reply to a message by the user or give username of user you want to {action}..."
        )
        return
    except UserRecordError as e:
        update.effective_message.reply_text(e.message)
        return

    # check if user is trying to ban the bot
    if kwargs["user_id"] == context.bot.id:
        update.effective_message.reply_markdown(f"Try to {action} me again, I'll meow meow your buttocks.")
        return

    user = update.effective_chat.get_member(kwargs["user_id"])

    # check if user is in the group
    if user.status == "left":
        update.effective_message.reply_text(
            f"If you can't steal catnip from an empty can, you can't {action} someone who isn't in the group."
        )
        return

    # check if user is trying to ban an admin
    if user.status in ("administrator", "creator"):
        update.effective_message.reply_markdown(f"Try to {action} an admin again, I might just {action} __you__.")
        return

    # get datetime till when we have to mute user
    if action == "ban" and context.args:
        try:
            kwargs["until_date"] = get_datetime_form_args(context.args, username)
        except TimeFormatException:
            update.effective_message.reply_markdown(
                "Please give the unit of time as one of the following\n\n`m` = minutes\n`h` = hours\n`d` = days"
            )
            return
        except ValueError:
            update.effective_message.reply_text("Time needs to be a number, baka!")
            return

    # announce ban
    reply = f"{'Banned' if action == 'ban' else 'Kicked'} @{username} to the litter :smiling_face_with_horns:"
    if action == "ban":
        reply += "\nIf you want to be added again, bribe an admin with some catnip to add you..."
        if kwargs.get("until_date"):
            reply += f"\n\nBanned till <code>{kwargs['until_date'].strftime('%c')} UTC</code>"

    if action == "ban":
        # if user is being banned, troll them with banhammer video
        with open(join(dirname(__file__), "assets", "ban.mp4"), "rb") as f:
            update.effective_message.reply_video(video=f, caption=emojize(reply))
    else:
        update.effective_message.reply_markdown(emojize(reply))

    # ban user
    context.bot.ban_chat_member(**kwargs)
    if action == "kick":
        context.bot.unban_chat_member(kwargs["chat_id"], kwargs["user_id"])


@bot_action("ban")
@for_chat_types("supergroup", "channel")
@check_user_admin
@check_bot_admin
@can_restrict
def ban(update: Update, context: CallbackContext):
    """
    ban a user from a chat
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    ban_kick(update, context)


@bot_action("unban")
@for_chat_types("supergroup", "channel")
@check_user_admin
@check_bot_admin
@can_restrict
def unban(update: Update, context: CallbackContext):
    """
    unban a user from a chat
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    # kwargs to pass to the ban_chat_member function call
    kwargs = {"chat_id": update.effective_chat.id}

    # get user to unban
    try:
        kwargs["user_id"], username = get_user_from_message(update.effective_message)
    except UserError:
        update.effective_message.reply_text(
            f"Reply to a message by the user or give username of user you want to unban..."
        )
        return
    except UserRecordError as e:
        update.effective_message.reply_text(e.message)
        return

    context.bot.unban_chat_member(kwargs["chat_id"], kwargs["user_id"])

    update.effective_message.reply_text(
        f"Someone go to the litter and tell {username} that he's been unbanned....\n\nfor now."
    )


@bot_action("kick")
@for_chat_types("supergroup", "channel")
@check_user_admin
@check_bot_admin
@can_restrict
def kick(update: Update, context: CallbackContext):
    """
    kick a user from a chat
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    ban_kick(update, context)


@bot_action("promote")
@for_chat_types("supergroup", "channel")
@check_user_admin
@check_bot_admin
def promote(update: Update, context: CallbackContext):
    """
    Promote a user to give him admin rights
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    # check if user has enough perms
    if update.effective_chat.id not in get_command_exception_chats("admin"):
        user = update.effective_chat.get_member(update.effective_user.id)
        if not user.can_promote_members and user.status != "creator":
            update.effective_message.reply_markdown(
                "Ask your sugar daddy to give you perms required to use the method `CanPromoteMembers`."
            )
            return

    # get bot member object to check it's perms
    bot: ChatMember = update.effective_chat.get_member(context.bot.id)

    # check if bot can promote users
    if not bot.can_promote_members:
        update.effective_message.reply_markdown(
            "Ask your sugar daddy to give me perms required to use the method `CanPromoteMembers`."
        )
        return

    # get member to promote
    try:
        user_id, username = get_user_from_message(update.effective_message)
    except UserError:
        update.effective_message.reply_text(
            "Reply to a message by the user or give username of user you want to promote..."
        )
        return
    except UserRecordError as e:
        update.effective_message.reply_text(e.message)
        return

    # promote member
    reply = ""
    try:
        context.bot.promote_chat_member(
            chat_id=update.effective_chat.id,
            user_id=user_id,
            can_change_info=bot.can_change_info,
            can_post_messages=bot.can_post_messages,
            can_edit_messages=bot.can_edit_messages,
            can_delete_messages=bot.can_delete_messages,
            can_invite_users=bot.can_invite_users,
            can_restrict_members=bot.can_restrict_members,
            can_pin_messages=bot.can_pin_messages,
            can_promote_members=bot.can_promote_members,
        )
        reply += f"Everyone say NyaHello to {mention_markdown(user_id, username)}, our new admin!"

        # get all args other than the username
        useful_args = []
        for arg in context.args:
            if username not in arg:
                useful_args.append(arg)

        if useful_args:
            title = " ".join(useful_args)
            context.bot.set_chat_administrator_custom_title(update.effective_chat.id, user_id, title)
            reply += f"\nThey have been granted the title of `{title}`."

        update.effective_message.reply_markdown(reply.strip())

    except BadRequest:
        update.effective_message.reply_text(
            "This cat can't meow at it's superiors.... and neither can I change their perms or title."
        )


@bot_action("demote")
@for_chat_types("supergroup", "channel")
@check_user_admin
@check_bot_admin
def demote(update: Update, context: CallbackContext):
    """
    Demote a user to remove admin rights
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    # check if user has enough perms
    if update.effective_chat.id not in get_command_exception_chats("admin"):
        user = update.effective_chat.get_member(update.effective_user.id)
        if not user.can_promote_members and user.status != "creator":
            update.effective_message.reply_markdown(
                "Ask your sugar daddy to give you perms required to use the method `CanPromoteMembers`."
            )
            return

    # get bot member object to check it's perms
    bot: ChatMember = update.effective_chat.get_member(context.bot.id)

    # check if bot can demote users
    if not bot.can_promote_members:
        update.effective_message.reply_markdown(
            "Ask your sugar daddy to give me perms required to use the method `CanPromoteMembers`."
        )
        return

    # get member to demote
    try:
        user_id, username = get_user_from_message(update.effective_message)
    except UserError:
        update.effective_message.reply_text(
            "Reply to a message by the user or give username of user you want to demote..."
        )
        return
    except UserRecordError as e:
        update.effective_message.reply_text(e.message)
        return

    # demote member
    if update.effective_chat.get_member(user_id).status != "administrator":
        update.effective_message.reply_text("What are you gonna demote a pleb to?")
        return

    try:
        context.bot.promote_chat_member(
            chat_id=update.effective_chat.id,
            user_id=user_id,
            can_change_info=False,
            can_post_messages=False,
            can_edit_messages=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False,
        )

        update.effective_message.reply_markdown(
            emojize(
                f"{mention_markdown(user_id, username)} has been thrown down from the council of admins to rot with the"
                f" rest of you plebs :grinning_cat_face_with_smiling_eyes:"
            )
        )

    except BadRequest:
        update.effective_message.reply_text(
            "This cat can't meow at it's superiors.... and neither can I change their perms or title."
        )


@bot_action("pin")
@for_chat_types("supergroup", "channel")
@check_user_admin
@check_bot_admin
def pin(update: Update, context: CallbackContext):
    """
    Pin a message in the chat
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    # check if user has enough perms
    if update.effective_chat.id not in get_command_exception_chats("admin"):
        user = update.effective_chat.get_member(update.effective_user.id)
        if not user.can_pin_messages and user.status != "creator":
            update.effective_message.reply_markdown(
                "Ask your sugar daddy to give you perms required to use the method `CanPinMessages`."
            )
            return

    # check if bot has perms to pin a message
    if (
        update.effective_chat.type == "supergroup"
        and not update.effective_chat.get_member(context.bot.id).can_pin_messages
    ) or (
        update.effective_chat.type == "channel"
        and not update.effective_chat.get_member(context.bot.id).can_edit_messages
    ):
        update.effective_message.reply_text(
            "Bribe your sugar daddy with some catnip and ask him to allow me to pin messages..."
        )
        return

    # check if there is a message to pin
    if not update.effective_message.reply_to_message:
        update.effective_message.reply_text("I'm a cat, not a psychic! Reply to the message you want to pin...")
        return

    # for future usage
    add_user(
        user_id=update.effective_message.reply_to_message.from_user.id,
        username=update.effective_message.reply_to_message.from_user.username,
    )

    # Don't always loud pin
    if context.args:
        disable_notification = context.args[0].lower() in ("silent", "quiet")
    else:
        disable_notification = None

    # pin the message
    context.bot.pin_chat_message(
        update.effective_chat.id,
        update.effective_message.reply_to_message.message_id,
        disable_notification=disable_notification,
    )


__mod_name__ = "Admin"

__exception_desc__ = (
    "If you add an exception to `admin`, I will allow admins to execute commands even if they don't have the "
    "individual permissions."
)

__commands__ = [
    CommandDescription(
        command="pin", args="<reply> [silent|quiet]", description="pin replied message in the chat", is_admin=True
    ),
    CommandDescription(
        command="promote",
        args="<reply|username> [<title>]",
        description="promotes a user (whose username you've given as argument, or whose message you are quoting) to admin",
        is_admin=True,
    ),
    CommandDescription(
        command="demote",
        args="<reply|username>",
        description="demotes an admin (whose username you've given as argument, or whose message you are quoting)",
        is_admin=True,
    ),
    CommandDescription(
        command="mute",
        args="<reply|username> [x<m|h|d>]",
        description=(
            "mutes a user (whose username you've given as argument, or whose message you are quoting) for x time, "
            "or until they are un-muted. m = minutes, h = hours, d = days."
        ),
        is_admin=True,
    ),
    CommandDescription(
        command="unmute",
        args="<reply|username>",
        description="un-mutes a user (whose username you've given as argument, or whose message you are quoting)",
        is_admin=True,
    ),
    CommandDescription(
        command="ban",
        args="<reply|username> [x<m|h|d>]",
        description=(
            "ban a user from the chat (whose username you've given as argument, or whose message you are quoting) "
            "for x time, or until they are added back. m = minutes, h = hours, d = days."
        ),
        is_admin=True,
    ),
    CommandDescription(
        command="unban",
        args="<reply|username>",
        description=(
            "unban a user from the chat (whose username you've given as argument, or whose message you are quoting)."
        ),
        is_admin=True,
    ),
    CommandDescription(
        command="kick",
        args="<reply|username>",
        description="kick a user from the chat (whose username you've given as argument, or whose message you are quoting)",
        is_admin=True,
    ),
]

# create handlers
dispatcher.add_handler(CommandHandler("promote", promote, run_async=True))
dispatcher.add_handler(CommandHandler("demote", demote, run_async=True))
dispatcher.add_handler(CommandHandler("mute", mute, run_async=True))
dispatcher.add_handler(CommandHandler("unmute", unmute, run_async=True))
dispatcher.add_handler(CommandHandler("ban", ban, run_async=True))
dispatcher.add_handler(CommandHandler("unban", unban, run_async=True))
dispatcher.add_handler(CommandHandler("kick", kick, run_async=True))
dispatcher.add_handler(CommandHandler("pin", pin, run_async=True))
