from telegram import Update
from telegram.ext import run_async, CallbackContext

from telebot.modules.db.exceptions import get_command_exception_chats


@run_async
def mute(update: Update, context: CallbackContext):
    """
    Mute a user, temporarily or permanently
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    # check if user is admin
    user = update.effective_chat.get_member(update.effective_user.id)
    if user.status not in ('administrator', 'creator') and update.effective_chat.type != "private":
        update.effective_message.reply_text("Get some admin privileges before you try to order me around, baka!")
        return

    if update.effective_chat.id not in get_command_exception_chats("mute") and not user.can_restric_members:
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
