import math
import os
from os import remove
from urllib.request import urlretrieve

from PIL import Image
from decouple import config
from emoji import emojize
from telegram import Update, TelegramError, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import run_async, CallbackContext, CommandHandler
from telegram.utils.helpers import escape_markdown

from telebot import dispatcher, log
from telebot.modules.sql.exceptions_sql import get_command_exception_chats


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


def _resize(kang_sticker):
    im = Image.open(kang_sticker)
    maxsize = (512, 512)
    if (im.width and im.height) < 512:
        size1 = im.width
        size2 = im.height
        if im.width > im.height:
            scale = 512 / size1
            size1new = 512
            size2new = size2 * scale
        else:
            scale = 512 / size2
            size1new = size1 * scale
            size2new = 512
        size1new = math.floor(size1new)
        size2new = math.floor(size2new)
        size_new = (size1new, size2new)
        im = im.resize(size_new)
    else:
        im.thumbnail(maxsize)

    return im


def _make_pack(msg, user, png_sticker, emoji, bot, pack_name, pack_num):
    name = user.first_name
    name = name[:50]

    try:
        extra_version = " " + str(pack_num) if pack_num > 0 else ""
        success = bot.create_new_sticker_set(
            user.id, pack_name, f"{name}s kang pack" + extra_version, png_sticker=png_sticker, emojis=emoji
        )

    except TelegramError as e:

        if e.message == "Sticker set name is already occupied":
            msg.reply_markdown(f"Your pack can be found [here](t.me/addstickers/{pack_name})")

        elif e.message == "Peer_id_invalid":
            msg.reply_text(
                "Contact me in PM first.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Start", url=f"t.me/{bot.username}")]]),
            )

        elif e.message == "Internal Server Error: created sticker set not found (500)":
            msg.reply_markdown(f"Sticker pack successfully created. Get it [here](t.me/addstickers/{pack_name})")

        return

    if success:
        msg.reply_markdown(f"Sticker pack successfully created. Get it [here](t.me/addstickers/{pack_name})")

    else:
        msg.reply_text("Failed to create sticker pack. Possibly due to blek mejik.")


@run_async
def kang(update: Update, context: CallbackContext):
    log(update, "kang")

    if update.effective_user.id not in config(
        "SUPERUSERS", cast=lambda x: map(int, x.split(","))
    ) and update.effective_chat.id in get_command_exception_chats("kang"):
        return

    msg = update.effective_message
    user = update.effective_user
    bot = context.bot

    # get sticker pack of user
    pack_num = 0
    pack_name = "a" + str(user.id) + "_by_" + bot.username
    max_stickers = 120

    try:
        sticker_set = bot.get_sticker_set(pack_name)
        while len(sticker_set.stickers) >= max_stickers:
            try:
                pack_num += 1
                pack_name = "a" + str(pack_num) + "_" + str(user.id) + "_by_" + bot.username
                sticker_set = bot.get_sticker_set(pack_name)
            except TelegramError:
                break

    except TelegramError:
        pass

    kang_sticker = "kang_sticker.png"

    # If user has replied to some message
    if msg.reply_to_message:

        # get sticker file
        if msg.reply_to_message.sticker:
            file_id = msg.reply_to_message.sticker.file_id
        elif msg.reply_to_message.photo:
            file_id = msg.reply_to_message.photo[-1].file_id
        elif msg.reply_to_message.document:
            file_id = msg.reply_to_message.document.file_id
        else:
            msg.reply_text("Nyet, can't kang that. Even if you bribe me with catnip.")
            return

        # download sticker file
        kang_file = bot.get_file(file_id)
        kang_file.download('kang_sticker.png')

        # get emoji(s) for sticker
        if context.args:
            sticker_emoji = str(context.args[0])
        elif msg.reply_to_message.sticker and msg.reply_to_message.sticker.emoji:
            sticker_emoji = msg.reply_to_message.sticker.emoji
        else:
            sticker_emoji = "🤔"

        # resize image and add to sticker pack
        try:
            im = _resize(kang_sticker)

            if not msg.reply_to_message.sticker:
                im.save(kang_sticker, "PNG")

            bot.add_sticker_to_set(
                user_id=user.id, name=pack_name, png_sticker=open('kang_sticker.png', 'rb'), emojis=sticker_emoji
            )
            msg.reply_markdown(
                f"Sticker successfully added to [pack](t.me/addstickers/{pack_name})" + f"\nEmoji is: {sticker_emoji}"
            )

        except OSError:
            msg.reply_text("I can only kang images.\nAnd catnip. If I'm feeling like it.")
            return

        except TelegramError as e:
            if e.message == "Stickerset_invalid":
                _make_pack(msg, user, open('kang_sticker.png', 'rb'), sticker_emoji, bot, pack_name, pack_num)

            elif e.message == "Sticker_png_dimensions":
                im.save(kang_sticker, "PNG")
                bot.add_sticker_to_set(
                    user_id=user.id, name=pack_name, png_sticker=open('kang_sticker.png', 'rb'), emojis=sticker_emoji
                )
                msg.reply_markdown(
                    f"Sticker successfully added to [pack](t.me/addstickers/{pack_name})"
                    + f"\nEmoji is: {sticker_emoji}"
                )

            elif e.message == "Invalid sticker emojis":
                msg.reply_text("Invalid emoji(s).")

            elif e.message == "Stickers_too_much":
                msg.reply_text("Meowtastic news! This loser just maxed out his pack size. Press F to pay respecc.")

            elif e.message == "Internal Server Error: sticker set not found (500)":
                msg.reply_markdown(
                    f"Sticker successfully added to [pack](t.me/addstickers/{pack_name})" + "\n"
                    "Emoji is:" + " " + sticker_emoji
                )

    elif context.args:
        try:
            try:
                url_emoji = msg.text.split(" ")
                png_sticker = url_emoji[1]
                sticker_emoji = url_emoji[2]
            except IndexError:
                sticker_emoji = "🤔"

            urlretrieve(png_sticker, kang_sticker)
            im = _resize(kang_sticker)
            im.save(kang_sticker, "PNG")

            msg.reply_photo(photo=open('kang_sticker.png', 'rb'))
            bot.add_sticker_to_set(
                user_id=user.id, name=pack_name, png_sticker=open('kang_sticker.png', 'rb'), emojis=sticker_emoji
            )
            msg.reply_markdown(
                f"Sticker successfully added to [pack](t.me/addstickers/{pack_name})" + f"\nEmoji is: {sticker_emoji}"
            )

        except OSError:
            msg.reply_text("I can only kang images.\nAnd catnip. If I'm feeling like it.")
            return

        except TelegramError as e:
            if e.message == "Stickerset_invalid":
                _make_pack(msg, user, open('kang_sticker.png', 'rb'), sticker_emoji, bot, pack_name, pack_num)

            elif e.message == "Sticker_png_dimensions":
                im.save(kang_sticker, "PNG")
                bot.add_sticker_to_set(
                    user_id=user.id, name=pack_name, png_sticker=open('kang_sticker.png', 'rb'), emojis=sticker_emoji
                )
                msg.reply_markdown(
                    f"Sticker successfully added to [pack](t.me/addstickers/{pack_name})"
                    + "\n"
                    + "Emoji is:"
                    + " "
                    + sticker_emoji
                )

            elif e.message == "Invalid sticker emojis":
                msg.reply_text("Invalid emoji(s).")

            elif e.message == "Stickers_too_much":
                msg.reply_text("Meowtastic news! This loser just maxed out his pack size. Press F to pay respecc.")

            elif e.message == "Internal Server Error: sticker set not found (500)":
                msg.reply_markdown(
                    f"Sticker successfully added to [pack](t.me/addstickers/{pack_name})" + "\n"
                    "Emoji is:" + " " + sticker_emoji
                )

    else:
        reply = "Please reply to a sticker, or image to kang it!"

        try:
            first_pack_name = "a" + str(user.id) + "_by_" + bot.username
            bot.get_sticker_set(first_pack_name)
            reply += f"\nOh, by the way. here are your packs:\n[pack](t.me/addstickers/{first_pack_name})\n"
            if pack_num > 0:
                for i in range(1, pack_num + 1):
                    reply += f"[pack{i}](t.me/addstickers/{pack_name})\n"

        except TelegramError:
            pass

        msg.reply_markdown(reply)

    if os.path.isfile("kang_sticker.png"):
        os.remove("kang_sticker.png")


__help__ = """
- /stickerid <reply> : reply to a sticker to me to tell you its file ID.
- /getsticker <reply> : reply to a sticker to me to upload its raw PNG file.
- /kang <reply> [<emojis>] : reply to a sticker to add it to your pack.
"""

__mod_name__ = "Stickers"

dispatcher.add_handler(CommandHandler("stickerid", sticker_id))
dispatcher.add_handler(CommandHandler("getsticker", get_sticker))
dispatcher.add_handler(CommandHandler('kang', kang))
