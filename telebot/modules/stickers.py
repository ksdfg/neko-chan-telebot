from os import remove

from emoji import emojize
from telegram import Update
from telegram.ext import run_async, CallbackContext, CommandHandler
from telegram.utils.helpers import escape_markdown

from telebot import dispatcher, log


@run_async
def sticker_id(update: Update, context: CallbackContext):
    log(update, "sticker id")

    rep_msg = update.effective_message.reply_to_message
    if rep_msg and rep_msg.sticker:
        update.effective_message.reply_markdown("Sticker ID:\n```" + escape_markdown(rep_msg.sticker.file_id) + "```",)
    else:
        update.effective_message.reply_text("Please reply to a sticker to get its ID.")


@run_async
def get_sticker(update: Update, context: CallbackContext):
    log(update, "get sticker")

    rep_msg = update.effective_message.reply_to_message
    chat_id = update.effective_chat.id

    if rep_msg and rep_msg.sticker:
        # check if sticker is animated, fugg off if it is
        if rep_msg.sticker.is_animated:
            update.effective_message.reply_text(
                f"Sorry, cannyot get animated stickers for now {emojize(':crying_cat_face:', use_aliases=True)} I can meow tho..."
            )

        else:
            # download file
            file_id = rep_msg.sticker.file_id
            new_file = context.bot.get_file(file_id)
            new_file.download(f'{file_id}.png')

            # send picture
            context.bot.send_document(chat_id, document=open(f'{file_id}.png', 'rb'))

            # delete locally created image
            remove(f'{file_id}.png')

    else:
        update.effective_message.reply_text("Please reply to a sticker for me to upload its PNG.")


__help__ = """
- /stickerid: reply to a sticker to me to tell you its file ID.
- /getsticker: reply to a sticker to me to upload its raw PNG file.
"""

__mod_name__ = "Stickers"

dispatcher.add_handler(CommandHandler("stickerid", sticker_id))
dispatcher.add_handler(CommandHandler("getsticker", get_sticker))
