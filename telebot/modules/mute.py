from datetime import datetime, timedelta
from functools import wraps
from typing import Callable

from emoji import emojize
from telegram import Update, ChatPermissions
from telegram.ext import run_async, CallbackContext, CommandHandler

from telebot import dispatcher
from telebot.functions import check_user_admin, check_bot_admin
from telebot.modules.db.exceptions import get_command_exception_chats


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
            if not update.effective_chat.get_member(update.effective_user.id).can_restrict_members:
                update.effective_message.reply_markdown(
                    "Ask your sugar daddy to give you perms required to use the method `CanRestrictMembers`."
                )
                return

        else:
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
    bot = update.effective_chat.get_member(context.bot.id)
    user = update.effective_chat.get_member(update.effective_user.id)

    # kwargs to pass to the restrict_chat_member function call
    kwargs = {
        'chat_id': update.effective_chat.id,
        'permissions': ChatPermissions(
            can_send_messages=False,
            can_send_media_messages=False,
            can_send_other_messages=False,
            can_send_polls=False,
            can_add_web_page_previews=False,
            can_change_info=user.can_change_info,
            can_invite_users=user.can_invite_users,
            can_pin_messages=user.can_pin_messages,
        ),
    }

    # get user to mute
    if update.effective_message.reply_to_message:
        kwargs['user_id'] = update.effective_message.reply_to_message.from_user
        # check if user is trying to mute an admin
        if update.effective_chat.get_member(kwargs['user_id']).status not in ('administrator', 'creator'):
            update.effective_message.reply_text("I can't mute an admin, baka!")
    else:
        update.effective_message.reply_text("Reply to a message by the user you want to mute...")
        return

    if context.args:
        # get datetime till when we have to mute user
        try:
            time, unit = float(context.args[0][:-1]), context.args[0][-1]
            if unit == 'd':
                kwargs['until_date'] = datetime.now() + timedelta(days=time)
            elif unit == 'h':
                kwargs['until_date'] = datetime.now() + timedelta(hours=time)
            elif unit == 'm':
                kwargs['until_date'] = datetime.now() + timedelta(minutes=time)
            else:
                update.effective_message.reply_markdown(
                    "Please give the unit of time as one of the following\n\n`m` = minutes\n`h` = hours\n`d` = days"
                )
                return
        except ValueError:
            update.effective_message.reply_text("Time needs to be a number, baka!")
            return

    context.bot.restrict_chat_member(**kwargs)

    reply = (
        f"Sewed up @{update.effective_message.reply_to_message.from_user.username}'s mouth :smiling_face_with_horns:"
        + "\nIf you want to be un-muted, bribe an admin with some catnip to do it for you..."
    )
    if 'until_time' in kwargs.keys():
        reply += f" or wait till `{kwargs['until_date'].strftime('%c')}`"
    update.effective_message.reply_markdown(emojize(reply))


__help__ = """
***Admin only :***
- /mute `<reply> [x<m|h|d>]`: mutes a user (whose message you are replying to) for x time, or until they are unmuted. m = minutes, h = hours, d = days.
- /unmute `<reply>`: unmutes a user (whose message you are replying to)
"""

__mod_name__ = "Muting"

dispatcher.add_handler(CommandHandler("mute", mute))
