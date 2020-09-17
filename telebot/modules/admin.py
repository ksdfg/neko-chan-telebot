from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Callable

from emoji import emojize
from telegram import Update, ChatPermissions, MessageEntity, ChatMember
from telegram.error import BadRequest
from telegram.ext import run_async, CallbackContext, CommandHandler
from telegram.utils.helpers import escape_markdown

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

    # noinspection DuplicatedCode
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
            f"Sewed up @{escape_markdown(update.effective_message.reply_to_message.from_user.username)}'s mouth "
            f":smiling_face_with_horns:\nIf you want to be un-muted, bribe an admin with some catnip to do it for you..."
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


@run_async
@check_user_admin
@check_bot_admin
@can_restrict
def ban(update: Update, context: CallbackContext):
    """
    ban a user from a chat
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    action = "ban" if update.effective_message.text.split(None, 1)[0] == "/ban" else "kick"
    log(update, action)

    # kwargs to pass to the ban_chat_member function call
    kwargs = {'chat_id': update.effective_chat.id}

    # get user to ban
    if update.effective_message.reply_to_message:
        kwargs['user_id'] = update.effective_message.reply_to_message.from_user.id

        # check if user is trying to ban the bot
        if kwargs['user_id'] == context.bot.id:
            update.effective_message.reply_markdown(f"Try to {action} me again, I'll meow meow your buttocks.")
            return

        # check if user is trying to ban an admin
        user = update.effective_chat.get_member(kwargs['user_id'])
        if user.status in ('administrator', 'creator'):
            update.effective_message.reply_markdown(f"Try to {action} an admin again, I might just {action} __you__.")
            return

    else:
        update.effective_message.reply_text(f"Reply to a message by the user you want to {action}...")
        return

    # noinspection DuplicatedCode
    if context.args:
        # get datetime till when we have to ban user
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

    # ban user
    context.bot.kick_chat_member(**kwargs)
    if action == "kick" and 'until_date' not in kwargs.keys():
        context.bot.unban_chat_member(kwargs['chat_id'], kwargs['user_id'])

    # announce ban
    reply = (
        f"{'Banned' if action == 'ban' else 'Kicked'} "
        f"@{escape_markdown(update.effective_message.reply_to_message.from_user.username)} to the litter "
        f":smiling_face_with_horns:"
    )
    if action == "ban":
        reply += "\nIf you want to be added again, bribe an admin with some catnip to add you..."
    if 'until_date' in kwargs.keys():
        reply += f"\n\nBanned till `{kwargs['until_date'].strftime('%c')} UTC`"

    update.effective_message.reply_markdown(emojize(reply))


@run_async
@check_user_admin
@check_bot_admin
def promote(update: Update, context: CallbackContext):
    """
    Promote a user to give him admin rights
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    # check if user has enough perms
    if update.effective_chat.type != "private" and update.effective_chat.id not in get_command_exception_chats("admin"):
        user = update.effective_chat.get_member(update.effective_user.id)
        if not user.can_promote_members and user.status != "creator":
            update.effective_message.reply_markdown(
                "Ask your sugar daddy to give you perms required to use the method `CanPromoteMembers`."
            )
            return

    # check if bot can promote users
    if (
        update.effective_chat.type != "private"
        and not update.effective_chat.get_member(context.bot.id).can_promote_members
    ):
        update.effective_message.reply_markdown(
            "Ask your sugar daddy to give me perms required to use the method `CanPromoteMembers`."
        )
        return

    log(update, "promote")

    # get member to promote
    if update.effective_message.reply_to_message:
        user_id = update.effective_message.reply_to_message.from_user.id
        # check if user is trying to mute an admin
        if update.effective_chat.get_member(user_id).status in ('administrator', 'creator'):
            update.effective_message.reply_markdown(
                "Thanks for trying to promote an admin. Maybe bring me some catnip you're high on next time?"
            )
            return
    else:
        update.effective_message.reply_text(f"Reply to a message by the user you want to promote...")
        return

    # get bot member object to check it's perms
    bot: ChatMember = update.effective_chat.get_member(context.bot.id)

    # promote member
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

    update.effective_message.reply_text(
        f"Everyone say NyaHello to @{update.effective_message.reply_to_message.from_user.username}, " f"our new admin"
    )


@run_async
@check_user_admin
@check_bot_admin
def pin(update: Update, context: CallbackContext):
    """
    Pin a message in the chat
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    # check if user has enough perms
    if update.effective_chat.type != "private" and update.effective_chat.id not in get_command_exception_chats("admin"):
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

    log(update, "pin")

    # check if there is a message to pin
    if not update.effective_message.reply_to_message:
        update.effective_message.reply_text("I'm a cat, not a psychic! Reply to the message you want to pin...")
        return

    # Don't always loud pin
    if context.args:
        disable_notification = context.args[0].lower() in ('silent', 'quiet')
    else:
        disable_notification = None

    # pin the message
    context.bot.pin_chat_message(
        update.effective_chat.id,
        update.effective_message.reply_to_message.message_id,
        disable_notification=disable_notification,
    )


@run_async
@check_user_admin
@check_bot_admin
def purge(update: Update, context: CallbackContext):
    """
    Delete all messages from quoted message
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    # check if user has enough perms
    if update.effective_chat.type != "private" and update.effective_chat.id not in get_command_exception_chats("admin"):
        user = update.effective_chat.get_member(update.effective_user.id)
        if not user.can_delete_messages and user.status != "creator":
            update.effective_message.reply_markdown(
                "Ask your sugar daddy to give you perms required to use the method `CanDeleteMessages`."
            )
            return

    # check if bot has perms to delete a message
    if (
        update.effective_chat.type != "private"
        and not update.effective_chat.get_member(context.bot.id).can_delete_messages
    ):
        update.effective_message.reply_text(
            "Bribe your sugar daddy with some catnip and ask him to allow me to delete messages..."
        )
        return

    log(update, "purge")

    # check if start point is given
    if not update.effective_message.reply_to_message:
        update.effective_message.reply_text(
            "I'm a cat, not a psychic! Reply to the message you want to start deleting from..."
        )
        return

    # delete messages
    for id_ in range(
        update.effective_message.message_id - 1, update.effective_message.reply_to_message.message_id - 1, -1
    ):
        try:
            context.bot.delete_message(update.effective_chat.id, id_)
        except BadRequest:
            continue

    update.effective_message.reply_text("Just like we do it in china....")


__help__ = """
***Admin only :***

- /promote `<reply>` : promotes a user (whose message you are replying to) to admin

- /mute `<reply> [x<m|h|d>]` : mutes a user (whose message you are replying to) for x time, or until they are un-muted. m = minutes, h = hours, d = days.

- /unmute `<reply|username>`: un-mutes a user (whose username you've given as argument, or whose message you are replying to)

- /ban `<reply> [x<m|h|d>]`: ban a user from the chat (whose message you are replying to) for x time, or until they are added back. m = minutes, h = hours, d = days.

- /kick `<reply> [x<m|h|d>]` : kick a user from the chat (whose message you are replying to) for x time, or until they are added back. m = minutes, h = hours, d = days.

- /purge `<reply>` : delete all messages from replied message to current one.

- /pin `<reply> [silent|quiet]` : pin replied message in the chat.

If you add an exception to `admin`, I will allow admins to execute commands even if they don't have the individual permissions.
"""

__mod_name__ = "Admin"

# create handlers
dispatcher.add_handler(CommandHandler("promote", promote))
dispatcher.add_handler(CommandHandler("mute", mute))
dispatcher.add_handler(CommandHandler("unmute", unmute))
dispatcher.add_handler(CommandHandler("ban", ban))
dispatcher.add_handler(CommandHandler("kick", ban))
dispatcher.add_handler(CommandHandler("pin", pin))
dispatcher.add_handler(CommandHandler("purge", purge))
