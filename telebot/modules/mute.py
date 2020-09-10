from telegram import Update
from telegram.ext import run_async, CallbackContext, CommandHandler

from telebot import dispatcher
from telebot.functions import check_user_admin, check_bot_admin
from telebot.modules.db.exceptions import get_command_exception_chats


@run_async
@check_user_admin
@check_bot_admin
def mute(update: Update, context: CallbackContext):
    """
    Mute a user, temporarily or permanently
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    bot = update.effective_chat.get_member(context.bot.id)
    user = update.effective_chat.get_member(update.effective_user.id)

    # check if user and bot have permissions to mute users
    if update.effective_chat.id not in get_command_exception_chats("mute"):
        if not bot.can_restrict_members:
            update.effective_message.reply_markdown(
                "Ask your sugar daddy to give me perms required to use the method `CanRestrictMembers`."
            )
            return
        if not user.can_restrict_members:
            update.effective_message.reply_markdown(
                "Ask your sugar daddy to give you perms required to use the method `CanRestrictMembers`."
            )
            return


__help__ = """
***Admin only :***
- /mute `<userhandle> [x<m|h|d>]`: mutes a user for x time, or until they are unmuted. (via handle, or reply). m = minutes, h = hours, d = days.
- /unmute `<userhandle>`: unmutes a user. Can also be used as a reply, muting the replied to user.
"""

__mod_name__ = "Muting"

dispatcher.add_handler(CommandHandler("mute", mute))
