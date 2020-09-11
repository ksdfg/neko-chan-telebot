from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Callable

from emoji import emojize
from telegram import Update, ChatPermissions, MessageEntity
from telegram.ext import run_async, CallbackContext, CommandHandler

from telebot import dispatcher
from telebot.functions import check_user_admin, check_bot_admin, log
from telebot.modules.db.exceptions import get_command_exception_chats
from telebot.modules.db.mute import add_muted_member, fetch_muted_member, remove_muted_member


def can_restrict(func: Callable):
    """
    Wrapper function for checking if user and bot has perms required for muting and un-muting
    :param func: The function this wraps over
    """

    @wraps(func)
    def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        if update.effective_chat.type != "private" and update.effective_chat.id not in get_command_exception_chats(
            "mute"
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


@run_async
@check_user_admin
@check_bot_admin
@can_restrict
def mute(update: Update, context: CallbackContext):
    """
    Mute a user, temporarily or permanently
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    log(update, "mute")

    # kwargs to pass to the restrict_chat_member function call
    kwargs = {'chat_id': update.effective_chat.id}

    # get user to mute
    if update.effective_message.reply_to_message:
        kwargs['user_id'] = update.effective_message.reply_to_message.from_user.id
        # check if user is trying to mute an admin
        user = update.effective_chat.get_member(kwargs['user_id'])
        if user.status in ('administrator', 'creator'):
            update.effective_message.reply_text("I can't mute an admin, baka!")
            return
    else:
        update.effective_message.reply_text("Reply to a message by the user you want to mute...")
        return

    # set muted permissions
    kwargs['permissions'] = ChatPermissions(
        can_send_messages=False,
        can_send_media_messages=False,
        can_send_other_messages=False,
        can_send_polls=False,
        can_add_web_page_previews=False,
        can_change_info=user.can_change_info,
        can_invite_users=user.can_invite_users,
        can_pin_messages=user.can_pin_messages,
    )

    if context.args:
        # get datetime till when we have to mute user
        try:
            time, unit = float(context.args[0][:-1]), context.args[0][-1]
            if unit == 'd':
                kwargs['until_date'] = datetime.now(tz=timezone.utc) + timedelta(days=time)
            elif unit == 'h':
                kwargs['until_date'] = datetime.now(tz=timezone.utc) + timedelta(hours=time)
            elif unit == 'm':
                kwargs['until_date'] = datetime.now(tz=timezone.utc) + timedelta(minutes=time)
            else:
                update.effective_message.reply_markdown(
                    "Please give the unit of time as one of the following\n\n`m` = minutes\n`h` = hours\n`d` = days"
                )
                return
        except ValueError:
            update.effective_message.reply_text("Time needs to be a number, baka!")
            return

    # add muted member in db
    if add_muted_member(
        chat=kwargs['chat_id'],
        user=kwargs['user_id'],
        username=update.effective_message.reply_to_message.from_user.username,
        until_date=kwargs['until_date'] if 'until_date' in kwargs.keys() else None,
    ):
        # mute member
        context.bot.restrict_chat_member(**kwargs)
        reply = (
            f"Sewed up @{update.effective_message.reply_to_message.from_user.username}'s mouth :smiling_face_with_horns:"
            + "\nIf you want to be un-muted, bribe an admin with some catnip to do it for you..."
        )
        if 'until_date' in kwargs.keys():
            reply += f" or wait till `{kwargs['until_date'].strftime('%c')} UTC`"
        update.effective_message.reply_markdown(emojize(reply))
    else:
        update.effective_message.reply_text("Couldn't save record in db....")


@run_async
@check_user_admin
@check_bot_admin
@can_restrict
def unmute(update: Update, context: CallbackContext):
    """
    Unmute a muted user
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    log(update, "un-mute")

    # kwargs to pass to the restrict_chat_member function call
    kwargs = {'chat_id': update.effective_chat.id}

    # get user to mute
    if update.effective_message.reply_to_message:
        kwargs['user_id'] = update.effective_message.reply_to_message.from_user.id
        username = update.effective_message.reply_to_message.from_user.username
    elif context.args:
        usernames = list(update.effective_message.parse_entities([MessageEntity.MENTION]).values())
        if usernames:
            kwargs['user_id'] = fetch_muted_member(chat=kwargs['chat_id'], username=usernames[0][1:])
            username = usernames[0][1:]
        else:
            update.effective_message.reply_text(
                "Reply to a message by the user or give username of user you want to unmute..."
            )
            return
    else:
        update.effective_message.reply_text(
            "Reply to a message by the user or give username of user you want to unmute..."
        )
        return

    # set muted permissions
    user = update.effective_chat.get_member(kwargs['user_id'])
    kwargs['permissions'] = ChatPermissions(
        can_send_messages=True,
        can_send_media_messages=True,
        can_send_other_messages=True,
        can_send_polls=True,
        can_add_web_page_previews=True,
        can_change_info=user.can_change_info,
        can_invite_users=user.can_invite_users,
        can_pin_messages=user.can_pin_messages,
    )

    # unmute member
    if remove_muted_member(chat=kwargs['chat_id'], user=kwargs['user_id']):
        context.bot.restrict_chat_member(**kwargs)
        update.effective_message.reply_text(f"@{username} can now go nyan nyan")
    else:
        update.effective_message.reply_text("Couldn't remove record from db....")


__help__ = """
***Admin only :***
- /mute `<reply> [x<m|h|d>]`: mutes a user (whose message you are replying to) for x time, or until they are unmuted. m = minutes, h = hours, d = days.
- /unmute `<reply|username>`: unmutes a user (whose username you've given as argument, or whose message you are replying to)
"""

__mod_name__ = "Muting"

dispatcher.add_handler(CommandHandler("mute", mute))
dispatcher.add_handler(CommandHandler("unmute", unmute))
