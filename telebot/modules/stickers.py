import math
import os
from os import remove
from urllib.request import urlretrieve
from uuid import uuid4

from PIL import Image
from decouple import config
from emoji import emojize
from telegram import Update, TelegramError, InlineKeyboardMarkup, InlineKeyboardButton, Bot, User
from telegram.error import BadRequest
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


def _get_pack_num_and_name(user: User, bot: Bot):
    pack_num = 0
    pack_name = "a" + str(user.id) + "_by_" + bot.username

    try:
        sticker_set = bot.get_sticker_set(pack_name)
        while len(sticker_set.stickers) >= 120:
            try:
                pack_num += 1
                pack_name = "a" + str(pack_num) + "_" + str(user.id) + "_by_" + bot.username
                sticker_set = bot.get_sticker_set(pack_name)
            except TelegramError:
                break

    except TelegramError:
        pass

    return pack_num, pack_name


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
            user.id, pack_name, f"{name}'s kang pack" + extra_version, png_sticker=png_sticker, emojis=emoji
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
        print(f"created pack {pack_name}")

    else:
        msg.reply_text("Failed to create sticker pack. Possibly due to blek mejik.")
        print(f"failed to create {pack_name}")


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
    pack_num, pack_name = _get_pack_num_and_name(user, bot)

    rendum_str = uuid4()
    kang_sticker = f"{user.id}_{rendum_str}_kang_sticker.png"

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
        kang_file.download(f'{user.id}_{rendum_str}_kang_sticker.png')

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
                user_id=user.id,
                name=pack_name,
                png_sticker=open(f'{user.id}_{rendum_str}_kang_sticker.png', 'rb'),
                emojis=sticker_emoji,
            )
            msg.reply_markdown(
                f"Sticker successfully added to [pack](t.me/addstickers/{pack_name})" + f"\nEmoji is: {sticker_emoji}"
            )

        except OSError:
            msg.reply_text("I can only kang images.\nAnd catnip. If I'm feeling like it.")
            return

        except TelegramError as e:
            if e.message == "Stickerset_invalid":
                _make_pack(
                    msg,
                    user,
                    open(f'{user.id}_{rendum_str}_kang_sticker.png', 'rb'),
                    sticker_emoji,
                    bot,
                    pack_name,
                    pack_num,
                )

            elif e.message == "Sticker_png_dimensions":
                im.save(kang_sticker, "PNG")
                bot.add_sticker_to_set(
                    user_id=user.id,
                    name=pack_name,
                    png_sticker=open(f'{user.id}_{rendum_str}_kang_sticker.png', 'rb'),
                    emojis=sticker_emoji,
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

            msg.reply_photo(photo=open(f'{user.id}_{rendum_str}_kang_sticker.png', 'rb'))
            bot.add_sticker_to_set(
                user_id=user.id,
                name=pack_name,
                png_sticker=open(f'{user.id}_{rendum_str}_kang_sticker.png', 'rb'),
                emojis=sticker_emoji,
            )
            msg.reply_markdown(
                f"Sticker successfully added to [pack](t.me/addstickers/{pack_name})" + f"\nEmoji is: {sticker_emoji}"
            )

        except OSError:
            msg.reply_text("I can only kang images.\nAnd catnip. If I'm feeling like it.")
            return

        except TelegramError as e:
            if e.message == "Stickerset_invalid":
                _make_pack(
                    msg,
                    user,
                    open(f'{user.id}_{rendum_str}_kang_sticker.png', 'rb'),
                    sticker_emoji,
                    bot,
                    pack_name,
                    pack_num,
                )

            elif e.message == "Sticker_png_dimensions":
                im.save(kang_sticker, "PNG")
                bot.add_sticker_to_set(
                    user_id=user.id,
                    name=pack_name,
                    png_sticker=open(f'{user.id}_{rendum_str}_kang_sticker.png', 'rb'),
                    emojis=sticker_emoji,
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

    if os.path.isfile(f"{user.id}_{rendum_str}_kang_sticker.png"):
        os.remove(f"{user.id}_{rendum_str}_kang_sticker.png")


@run_async
def migrate(update: Update, context: CallbackContext):
    log(update, "migrate pack")

    if update.effective_chat.id in get_command_exception_chats("migratepack"):
        return

    # check if there is a sticker to kang set from
    if (
        not update.effective_message.reply_to_message
        or not update.effective_message.reply_to_message.sticker
        or update.effective_message.reply_to_message.sticker.is_animated
    ):
        update.effective_message.reply_text(
            "Please reply to a non animated sticker that belongs to a pack you want to migrate"
        )
        return

    # get original set name
    og_set_name = update.effective_message.reply_to_message.sticker.set_name
    if og_set_name is None:
        update.effective_message.reply_text(
            "Please reply to a non animated sticker that belongs to a pack you want to migrate"
        )
        return

    # check if the sticker set already belongs to this bot
    if context.bot.username in og_set_name:
        update.effective_message.reply_markdown(f"This pack already belongs to `{context.bot.first_name}`...")
        return

    update.effective_message.reply_text("Please be patient, this little kitty's paws can only kang so fast....")

    # get original set data
    og_stickers_set = context.bot.get_sticker_set(og_set_name)
    og_set_title = og_stickers_set.title
    stickers = og_stickers_set.stickers

    # get the pack to migrate the stickers into
    pack_num, pack_name = _get_pack_num_and_name(update.effective_user, context.bot)
    appended_packs = [pack_name]  # list of packs the stickers were migrated into

    try:
        sticker_pack = context.bot.get_sticker_set(pack_name)
    except BadRequest:
        # download sticker
        context.bot.get_file(stickers[0].file_id).download(f"{update.effective_user.id}_{uuid4()}_migrate_sticker.png")

        # make pack
        try:
            _make_pack(
                None,
                update.effective_user,
                open(f"{update.effective_user.id}_{uuid4()}_migrate_sticker.png", 'rb'),
                stickers[0].emoji,
                context.bot,
                pack_name,
                pack_num,
            )
        # we don't want to send a message, hence passed msg as None to _make_pack
        # this leads to an AttributeError being raised
        except AttributeError:
            pass

        stickers = stickers[1:]  # because the first sticker is already in the new pack now
        sticker_pack = context.bot.get_sticker_set(pack_name)

    rendum_str = uuid4()

    for sticker in stickers:
        # download sticker
        context.bot.get_file(sticker.file_id).download(f"{update.effective_user.id}_{rendum_str}_migrate_sticker.png")

        # if current pack can still fit in more stickers
        if len(sticker_pack.stickers) < 120:
            try:
                context.bot.add_sticker_to_set(
                    user_id=update.effective_user.id,
                    name=pack_name,
                    png_sticker=open(f"{update.effective_user.id}_{rendum_str}_migrate_sticker.png", 'rb'),
                    emojis=sticker.emoji,
                )
            except BadRequest:
                # make new pack
                try:
                    _make_pack(
                        None,
                        update.effective_user,
                        open(f"{update.effective_user.id}_{rendum_str}_migrate_sticker.png", 'rb'),
                        sticker.emoji,
                        context.bot,
                        pack_name,
                        pack_num,
                    )
                # we don't want to send a message, hence passed msg as None to _make_pack
                # this leads to an AttributeError being raised
                except AttributeError:
                    pass

        # if current pack is full
        else:
            # new pack info
            pack_num += 1
            pack_name = "a" + str(pack_num) + "_" + str(update.effective_user.id) + "_by_" + context.bot.username
            appended_packs.append(pack_name)

            # make new pack
            try:
                _make_pack(
                    None,
                    update.effective_user,
                    open(f"{update.effective_user.id}_{rendum_str}_migrate_sticker.png", 'rb'),
                    sticker.emoji,
                    context.bot,
                    pack_name,
                    pack_num,
                )
            # we don't want to send a message, hence passed msg as None to _make_pack
            # this leads to an AttributeError being raised
            except AttributeError:
                pass

            sticker_pack = context.bot.get_sticker_set(pack_name)

    # send success reply to the user
    reply = (
        f"Done! Pack [{og_set_title}](t.me/addstickers/{og_set_name}) was migrated into :-"
        + f"\n[pack](t.me/addstickers/{appended_packs[0]})"
    )
    for index, pack in enumerate(appended_packs[1:]):
        reply += f"\n[pack {index + 1}](t.me/addstickers/{pack})"
    update.effective_message.reply_markdown(reply)

    # don't want rendum files on server
    if os.path.isfile(f"{update.effective_user.id}_{rendum_str}_migrate_sticker.png"):
        os.remove(f"{update.effective_user.id}_{rendum_str}_migrate_sticker.png")


__help__ = r"""
- /stickerid `<reply>` : reply to a sticker to me to tell you its file ID.
- /getsticker `<reply>` : reply to a sticker to me to upload its raw PNG file.
- /kang `<reply> [<emojis>]` : reply to a sticker to add it to your pack. Won't do anything if you have an exception set in the chat.
- /migratepack `<reply>` : reply to a sticker to migrate the entire sticker set it belongs to into your pack(s). Won't do anything if you have an exception set in the chat.
"""

__mod_name__ = "Stickers"

dispatcher.add_handler(CommandHandler("stickerid", sticker_id))
dispatcher.add_handler(CommandHandler("getsticker", get_sticker))
dispatcher.add_handler(CommandHandler('kang', kang))
dispatcher.add_handler(CommandHandler('migratepack', migrate))
