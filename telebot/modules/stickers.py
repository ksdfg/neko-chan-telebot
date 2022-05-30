import math
import os
from os import remove
from re import search
from typing import Tuple, IO, List
from urllib.request import urlretrieve
from uuid import uuid4

from PIL import Image
from emoji import emojize
from telegram import Update, TelegramError, InlineKeyboardMarkup, InlineKeyboardButton, Bot, User, Message, StickerSet
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler, MessageHandler, Filters
from telegram.utils.helpers import escape_markdown

from telebot import dispatcher, config
from telebot.modules.db.exceptions import get_command_exception_chats
from telebot.modules.db.users import add_user
from telebot.utils import bot_action, CommandDescription


@bot_action("sticker id")
def sticker_id(update: Update, context: CallbackContext) -> None:
    """
    Reply with the file ID of a given sticker
    :param update: object representing the incoming update.
    :param context: object containing data about the bot_action call.
    """
    rep_msg = update.effective_message.reply_to_message

    if rep_msg and rep_msg.sticker:
        # future usage
        add_user(
            user_id=update.effective_message.reply_to_message.from_user.id,
            username=update.effective_message.reply_to_message.from_user.username,
        )
        update.effective_message.reply_markdown("Sticker ID:\n```" + escape_markdown(rep_msg.sticker.file_id) + "```")

    else:
        update.effective_message.reply_text("Please reply to a sticker to get its ID.")


@bot_action("get sticker")
def get_sticker(update: Update, context: CallbackContext) -> None:
    """
    Reply with the PNG image as a document for a given sticker
    :param update: object representing the incoming update.
    :param context: object containing data about the bot_action call.
    """
    rep_msg = update.effective_message.reply_to_message
    chat_id = update.effective_chat.id

    if rep_msg and rep_msg.sticker:
        # future usage
        add_user(
            user_id=update.effective_message.reply_to_message.from_user.id,
            username=update.effective_message.reply_to_message.from_user.username,
        )

        # check if sticker is animated, fugg off if it is
        if rep_msg.sticker.is_animated:
            update.effective_message.reply_text(
                f"Sorry, cannyot get animated stickers for now {emojize(':crying_cat_face:', use_aliases=True)} I can meow tho..."
            )

        else:
            # download file
            file_id = rep_msg.sticker.file_id
            new_file = context.bot.get_file(file_id)
            new_file.download(f"{file_id}.png")

            # send picture
            context.bot.send_document(chat_id, document=open(f"{file_id}.png", "rb"))

            # delete locally created image
            remove(f"{file_id}.png")

    else:
        update.effective_message.reply_text("Please reply to a sticker for me to upload its PNG.")


def _get_packs(user: User, bot: Bot, is_animated: bool = False) -> List[Tuple[int, StickerSet]]:
    """
    get free pack into which we can add stickers
    :param user: the user whose packs we're fetching
    :param bot: the bot to ue to fetch these
    :param is_animated: True if it is an animated stickers pack, else False
    :return: List of tuples, with each tuple containing the pack number and the pack's StickerSet object
    """
    # default pack number and name of the first pack
    pack_num = 0
    pack_name = "a" + str(user.id)
    if is_animated:
        pack_name += "_animated"
    pack_name += "_by_" + bot.username

    # list of all the user's packs
    packs: List[Tuple[int, StickerSet]] = []

    max_stickers = 50 if is_animated else 120  # max number of stickers possible in a pack

    try:
        sticker_set = bot.get_sticker_set(pack_name)  # fetch the sticker pack
        packs.append((pack_num, sticker_set))  # append pack to list

        while len(sticker_set.stickers) >= max_stickers:
            # since fetched pack is full, get next pack
            try:
                pack_num += 1
                pack_name = "a" + str(pack_num) + "_" + str(user.id)
                if is_animated:
                    pack_name += "_animated"
                pack_name += "_by_" + bot.username

                sticker_set = bot.get_sticker_set(pack_name)
                packs.append((pack_num, sticker_set))  # append pack to list
            except TelegramError:
                # if the next pack doesn't exist yet, then this is the one to use
                break

    except TelegramError:
        # if user hasn't made any pack yet
        pass

    return packs


def _resize(kang_sticker: str) -> Image:
    """
    resize an image to fit the required dimensions for a sticker
    :param kang_sticker: file name where the image is stored
    :return: Image object of the resized image
    """
    im: Image = Image.open(kang_sticker)

    maxsize = (512, 512)
    if (im.width and im.height) < 512:
        # if the image is smaller than the required sticker size
        size1 = im.width
        size2 = im.height

        if im.width > im.height:
            # if width is bigger than height, then set width to 512 and scale height accordingly
            scale = 512 / size1
            size1new = 512
            size2new = size2 * scale
        else:
            # if height is bigger than width, then set height to 512 and scale width accordingly
            scale = 512 / size2
            size1new = size1 * scale
            size2new = 512

        # set image to new size
        size_new = (math.floor(size1new), math.floor(size2new))
        im = im.resize(size_new)

    else:
        # if image is bigger than sticker size, directly set thumbnail to fit in 512x512
        im.thumbnail(maxsize)

    return im


def _make_pack(
    msg: Message,
    user: User,
    sticker: IO,
    emoji: str,
    bot: Bot,
    pack_name: str,
    pack_num: int,
    is_animated: bool = False,
) -> None:
    """
    Make a new sticker pack
    :param msg: message to reply to on success or failure
    :param user: user to which the pack must belong
    :param sticker: sticker to add into the new sticker pack
    :param emoji: emojis for the above sticker
    :param bot: bot to use to create the bot
    :param pack_name: name of the new pack
    :param pack_num: number of the new pack
    :param is_animated: True if it's an animated stickers pack, else False
    """
    name = user.first_name[:50]

    try:
        # add an extra number to pack title if this isn't the first pack of the user
        extra_version = " " + str(pack_num) if pack_num > 0 else ""

        # create the pack
        if is_animated:
            success = bot.create_new_sticker_set(
                user.id, pack_name, f"{name}'s animated kang pack" + extra_version, tgs_sticker=sticker, emojis=emoji
            )
        else:
            success = bot.create_new_sticker_set(
                user.id, pack_name, f"{name}'s kang pack" + extra_version, png_sticker=sticker, emojis=emoji
            )

    except TelegramError as e:
        match e.message:
            case "Sticker set name is already occupied":
                msg.reply_markdown(f"Your pack can be found [here](t.me/addstickers/{pack_name})")

            case "Peer_id_invalid":
                msg.reply_text(
                    "Contact me in PM first.",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="Start", url=f"t.me/{bot.username}")]]
                    ),
                )

            case "Internal Server Error: created sticker set not found (500)":
                msg.reply_markdown(f"Sticker pack successfully created. Get it [here](t.me/addstickers/{pack_name})")

        return

    # send result to user
    if success:
        msg.reply_markdown(f"Sticker pack successfully created. Get it [here](t.me/addstickers/{pack_name})")
        print(f"created pack {pack_name}")
    else:
        msg.reply_text("Failed to create sticker pack. Possibly due to blek mejik.")
        print(f"failed to create {pack_name}")


@bot_action("kang")
def kang(update: Update, context: CallbackContext) -> None:
    """
    Add a sticker to user's pack
    :param update: object representing the incoming update.
    :param context: object containing data about the bot_action call.
    """
    # check for exception, but skip exception if user is a superuser
    if update.effective_user.id not in config.SUPERUSERS and update.effective_chat.id in get_command_exception_chats(
        "kang"
    ):
        return

    msg = update.effective_message
    user = update.effective_user
    bot = context.bot

    # get sticker pack of user
    try:
        is_animated = msg.reply_to_message.sticker.is_animated
    except AttributeError:
        is_animated = False
    packs = _get_packs(user, bot, is_animated)
    if packs:
        pack_num, pack = packs[-1]
        pack_name = pack.name
        pack_title = pack.title
    else:
        # default pack number and name of the first pack
        pack_num = 0
        pack_name = "a" + str(user.id)
        if is_animated:
            pack_name += "_animated"
        pack_name += "_by_" + bot.username
        pack_title = f"{user.id}'s "
        if is_animated:
            pack_title += "animated "
        pack_title += "kang pack"

    # file name to download sticker file as
    rendum_str = uuid4()
    kang_sticker = f"{user.id}_{rendum_str}_kang_sticker.{'tgs' if is_animated else 'png'}"

    # If user has replied to some message
    if is_animated:
        # future usage
        add_user(
            user_id=update.effective_message.reply_to_message.from_user.id,
            username=update.effective_message.reply_to_message.from_user.username,
        )

        # download sticker
        sticker = msg.reply_to_message.sticker
        context.bot.get_file(sticker.file_id).download(kang_sticker)

        # add to pack
        try:
            bot.add_sticker_to_set(
                user_id=user.id, name=pack_name, tgs_sticker=open(kang_sticker, "rb"), emojis=sticker.emoji
            )
            msg.reply_markdown(
                f"Sticker successfully added to [{pack_title}](t.me/addstickers/{pack_name})"
                + f"\nEmoji is: {sticker.emoji}"
            )

        except TelegramError as e:
            match e.message:
                case "Stickerset_invalid":
                    _make_pack(
                        msg, user, open(kang_sticker, "rb"), sticker.emoji, bot, pack_name, pack_num, is_animated
                    )

                case "Invalid sticker emojis":
                    msg.reply_text("Invalid emoji(s).")

                case "Stickers_too_much":
                    msg.reply_text("Meowtastic news! This loser just maxed out his pack size. Press F to pay respecc.")

                case "Internal Server Error: sticker set not found (500)":
                    msg.reply_markdown(
                        f"Sticker successfully added to [{pack_title}](t.me/addstickers/{pack_name})"
                        + f"\nEmoji is : {sticker.emoji}"
                    )

    elif msg.reply_to_message:
        # future usage
        add_user(
            user_id=update.effective_message.reply_to_message.from_user.id,
            username=update.effective_message.reply_to_message.from_user.username,
        )

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
        bot.get_file(file_id).download(kang_sticker)

        # get emoji(s) for sticker
        if context.args:
            sticker_emoji = str(context.args[0])
        elif msg.reply_to_message.sticker and msg.reply_to_message.sticker.emoji:
            sticker_emoji = msg.reply_to_message.sticker.emoji
        else:
            sticker_emoji = "🤔"

        # resize image
        im = _resize(kang_sticker)

        if not msg.reply_to_message.sticker:
            im.save(kang_sticker, "PNG")

        # add to sticker pack
        try:
            bot.add_sticker_to_set(
                user_id=user.id, name=pack_name, png_sticker=open(kang_sticker, "rb"), emojis=sticker_emoji
            )
            msg.reply_markdown(
                f"Sticker successfully added to [{pack_title}](t.me/addstickers/{pack_name})"
                + f"\nEmoji is: {sticker_emoji}"
            )

        except OSError:
            msg.reply_text("I can only kang images.\nAnd catnip. If I'm feeling like it.")
            return

        except TelegramError as e:
            match e.message:
                case "Stickerset_invalid":
                    _make_pack(msg, user, open(kang_sticker, "rb"), sticker_emoji, bot, pack_name, pack_num)

                case "Sticker_png_dimensions":
                    im.save(kang_sticker, "PNG")
                    bot.add_sticker_to_set(
                        user_id=user.id, name=pack_name, png_sticker=open(kang_sticker, "rb"), emojis=sticker_emoji
                    )
                    msg.reply_markdown(
                        f"Sticker successfully added to [{pack_title}](t.me/addstickers/{pack_name})"
                        + f"\nEmoji is: {sticker_emoji}"
                    )

                case "Invalid sticker emojis":
                    msg.reply_text("Invalid emoji(s).")

                case "Stickers_too_much":
                    msg.reply_text("Meowtastic news! This loser just maxed out his pack size. Press F to pay respecc.")

                case "Internal Server Error: sticker set not found (500)":
                    msg.reply_markdown(
                        f"Sticker successfully added to [{pack_title}](t.me/addstickers/{pack_name})"
                        + f"\nEmoji is : {sticker_emoji}"
                    )

    elif context.args:
        # get the emoji to use as sticker and the emojis to set to said sticker
        png_sticker = context.args[0]
        try:
            sticker_emoji = context.args[1]
        except IndexError:
            sticker_emoji = "🤔"

        # fetch the image for the emoji
        urlretrieve(png_sticker, kang_sticker)
        im = _resize(kang_sticker)
        im.save(kang_sticker, "PNG")

        # add to pack
        try:
            msg.reply_photo(photo=open(kang_sticker, "rb"))
            bot.add_sticker_to_set(
                user_id=user.id, name=pack_name, png_sticker=open(kang_sticker, "rb"), emojis=sticker_emoji
            )
            msg.reply_markdown(
                f"Sticker successfully added to [{pack_title}](t.me/addstickers/{pack_name})"
                + f"\nEmoji is: {sticker_emoji}"
            )

        except OSError:
            msg.reply_text("I can only kang images.\nAnd catnip. If I'm feeling like it.")
            return

        except TelegramError as e:
            match e.message:
                case "Stickerset_invalid":
                    _make_pack(msg, user, open(kang_sticker, "rb"), sticker_emoji, bot, pack_name, pack_num)

                case "Sticker_png_dimensions":
                    im.save(kang_sticker, "PNG")
                    bot.add_sticker_to_set(
                        user_id=user.id, name=pack_name, png_sticker=open(kang_sticker, "rb"), emojis=sticker_emoji
                    )
                    msg.reply_markdown(
                        f"Sticker successfully added to [{pack_title}](t.me/addstickers/{pack_name})"
                        + f"\nEmoji is : {sticker_emoji}"
                    )

                case "Invalid sticker emojis":
                    msg.reply_text("Invalid emoji(s).")

                case "Stickers_too_much":
                    msg.reply_text("Meowtastic news! This loser just maxed out his pack size. Press F to pay respecc.")

                case "Internal Server Error: sticker set not found (500)":
                    msg.reply_markdown(
                        f"Sticker successfully added to [{pack_title}](t.me/addstickers/{pack_name})"
                        + f"\nEmoji is : {sticker_emoji}"
                    )

    else:
        msg.reply_markdown("Please reply to a sticker, or image to kang it!")

    # delete stray files
    if os.path.isfile(kang_sticker):
        os.remove(kang_sticker)


@bot_action("migrate pack")
def migrate(update: Update, context: CallbackContext) -> None:
    """
    Migrate all stickers from a given pack into user's pack(s)
    :param update: object representing the incoming update.
    :param context: object containing data about the bot_action call.
    """
    # check if there is a sticker to kang set from
    if not update.effective_message.reply_to_message or not update.effective_message.reply_to_message.sticker:
        update.effective_message.reply_text("Please reply to a sticker that belongs to a pack you want to migrate!")
        return

    # future usage
    add_user(
        user_id=update.effective_message.reply_to_message.from_user.id,
        username=update.effective_message.reply_to_message.from_user.username,
    )

    # get original set name
    og_set_name = update.effective_message.reply_to_message.sticker.set_name
    if og_set_name is None:
        update.effective_message.reply_text("Please reply to a sticker that belongs to a pack you want to migrate!")
        return

    # check if the sticker set already belongs to this bot
    if search(f"{context.bot.username}$", og_set_name):
        update.effective_message.reply_markdown(f"This pack already belongs to `{context.bot.first_name}`...")
        return

    update.effective_message.reply_text("Please be patient, this little kitty's paws can only kang so fast....")

    # get original set data
    og_stickers_set = context.bot.get_sticker_set(og_set_name)
    og_set_title = og_stickers_set.title
    stickers = og_stickers_set.stickers
    is_animated = stickers[0].is_animated

    # get the pack to migrate the stickers into
    packs = _get_packs(update.effective_user, context.bot, is_animated)
    if packs:
        pack_num, pack = packs[-1]
        pack_name = pack.name
    else:
        # default pack number and name of the first pack
        pack_num = 0
        pack_name = "a" + str(update.effective_user.id)
        if is_animated:
            pack_name += "_animated"
        pack_name += "_by_" + update.effective_user.username
        pack_title = f"{update.effective_user.id}'s "
        if is_animated:
            pack_title += "animated "
        pack_title += "kang pack"

    # name of the file in which we locally store sticker
    rendum_str = uuid4()
    file = (
        f"{update.effective_user.id}_{rendum_str}_migrate_sticker.tgs"
        if is_animated
        else f"{update.effective_user.id}_{rendum_str}_migrate_sticker.png"
    )

    try:
        sticker_pack = context.bot.get_sticker_set(pack_name)
    except BadRequest:
        # download sticker
        context.bot.get_file(stickers[0].file_id).download(file)

        # make pack
        try:
            _make_pack(
                None,
                update.effective_user,
                open(file, "rb"),
                stickers[0].emoji,
                context.bot,
                pack_name,
                pack_num,
                is_animated,
            )
        # we don't want to send a message, hence passed msg as None to _make_pack
        # this leads to an AttributeError being raised
        except AttributeError:
            pass

        stickers = stickers[1:]  # because the first sticker is already in the new pack now
        sticker_pack = context.bot.get_sticker_set(pack_name)

    appended_packs = [sticker_pack]  # list of packs the stickers were migrated into

    max_stickers = 50 if is_animated else 120

    for sticker in stickers:
        # download sticker
        context.bot.get_file(sticker.file_id).download(file)

        # if current pack can still fit in more stickers
        if len(sticker_pack.stickers) < max_stickers:
            try:
                if is_animated:
                    context.bot.add_sticker_to_set(
                        user_id=update.effective_user.id,
                        name=pack_name,
                        tgs_sticker=open(file, "rb"),
                        emojis=sticker.emoji,
                    )
                else:
                    context.bot.add_sticker_to_set(
                        user_id=update.effective_user.id,
                        name=pack_name,
                        png_sticker=open(file, "rb"),
                        emojis=sticker.emoji,
                    )
            except BadRequest:
                # make new pack
                try:
                    _make_pack(
                        None,
                        update.effective_user,
                        open(file, "rb"),
                        sticker.emoji,
                        context.bot,
                        pack_name,
                        pack_num,
                        is_animated,
                    )
                # we don't want to send a message, hence passed msg as None to _make_pack
                # this leads to an AttributeError being raised
                except AttributeError:
                    pass

        # if current pack is full
        else:
            # new pack info
            pack_num += 1
            pack_name = "a" + str(pack_num) + "_" + str(update.effective_user.id)
            if is_animated:
                pack_name += "_animated"
            pack_name += "_by_" + context.bot.username

            # make new pack
            try:
                _make_pack(
                    None,
                    update.effective_user,
                    open(file, "rb"),
                    sticker.emoji,
                    context.bot,
                    pack_name,
                    pack_num,
                    is_animated,
                )
            # we don't want to send a message, hence passed msg as None to _make_pack
            # this leads to an AttributeError being raised
            except AttributeError:
                pass

            sticker_pack = context.bot.get_sticker_set(pack_name)
            appended_packs.append(sticker_pack)

    # send success reply to the user
    reply = f"Done! Pack [{og_set_title}](t.me/addstickers/{og_set_name}) was migrated into :-"
    for pack in appended_packs:
        reply += f"\n[{pack.title}](t.me/addstickers/{pack.name})"
    update.effective_message.reply_markdown(reply)

    # don't want rendum files on server
    if os.path.isfile(file):
        os.remove(file)


@bot_action("delete sticker")
def del_sticker(update: Update, context: CallbackContext) -> None:
    """
    Delete a sticker form one of the user's packs
    :param update: object representing the incoming update.
    :param context: object containing data about the bot_action call.
    """
    # check if there's anything to delete
    if not update.effective_message.reply_to_message or not update.effective_message.reply_to_message.sticker:
        update.effective_message.reply_text("Please reply to a sticker that belongs to a pack created by me")
        return

    # future usage
    add_user(
        user_id=update.effective_message.reply_to_message.from_user.id,
        username=update.effective_message.reply_to_message.from_user.username,
    )

    # check if the bot has perms to delete the sticker
    sticker = update.effective_message.reply_to_message.sticker
    set_name = sticker.set_name
    if not search(f"{context.bot.username}$", set_name):
        update.effective_message.reply_text("Please reply to a sticker that belongs to a pack created by me")
        return

    # get sticker set info (for better replies)
    set_title = context.bot.get_sticker_set(set_name).title

    # delete the sticker
    try:
        context.bot.delete_sticker_from_set(sticker.file_id)
    except BadRequest:
        update.effective_message.reply_text("Telegram seems to be high on catnip at the moment, try again in a while!")

    update.effective_message.reply_markdown(f"Deleted that sticker from [{set_title}](t.me/addstickers/{set_name}).")


@bot_action("list packs")
def packs(update: Update, context: CallbackContext):
    """
    List all the packs of a user
    :param update: object representing the incoming update.
    :param context: object containing data about the bot_action call.
    """
    # get all user packs
    packs = _get_packs(update.effective_user, context.bot, False) + _get_packs(update.effective_user, context.bot, True)

    if packs:
        reply = "Here's all your meowtastic packs!\n"
        for _, pack in packs:
            reply += f"\n[{pack.title}](t.me/addstickers/{pack.name})"

        update.effective_message.reply_markdown(reply)

    else:
        update.effective_message.reply_text(
            emojize("You have no packs yet! kang or migrate to make one :grinning_cat_face_with_smiling_eyes:")
        )


# dict of user - sticker to reorder
reorder = {}


@bot_action("reorder step 1")
def reorder1(update: Update, context: CallbackContext):
    """
    First step in reordering sticker in pack - take input of sticker who's position is to be changed
    :param update: object representing the incoming update.
    :param context: object containing data about the bot_action call.
    :return: 0 if successful to move on to next step, else -1 (ConversationHandler.END)
    """
    # check if there is a sticker to kang set from
    if not update.effective_message.reply_to_message or not update.effective_message.reply_to_message.sticker:
        update.effective_message.reply_text("Please reply to a sticker that belongs to a pack created by me")
        return ConversationHandler.END

    # future usage
    add_user(
        user_id=update.effective_message.reply_to_message.from_user.id,
        username=update.effective_message.reply_to_message.from_user.username,
    )

    # check if the bot has perms to delete the sticker
    sticker = update.effective_message.reply_to_message.sticker
    set_name = sticker.set_name
    if not search(f"{context.bot.username}$", set_name):
        update.effective_message.reply_text("Please reply to a sticker that belongs to a pack created by me")
        return ConversationHandler.END

    # if sticker position is given as arg, then set position and fugg off
    try:
        context.bot.set_sticker_position_in_set(
            update.effective_message.reply_to_message.sticker.file_id, int(context.args[0])
        )
        update.effective_message.reply_markdown(
            f"I have updated [{context.bot.get_sticker_set(set_name).title}](t.me/addstickers/{set_name})!"
        )
        return ConversationHandler.END
    except:
        pass

    # store sticker to reorder
    reorder[
        str(update.effective_user.id) + str(update.effective_chat.id)
    ] = update.effective_message.reply_to_message.sticker.file_id

    update.effective_message.reply_markdown(
        "Please send the sticker that is going to be on the `left` of this sticker __after__ the reorder, or /cancel to stop"
    )

    return 0


@bot_action("reorder step 2")
def reorder2(update: Update, context: CallbackContext):
    """
    Last step in reordering sticker in pack - take input of sticker which is now gonna be on the left of the reordered sticker
    :param update: object representing the incoming update.
    :param context: object containing data about the bot_action call.
    :return: 0, if wrong input is made, else -1 (ConversationHandler.END)
    """
    # check if there is a sticker
    if not update.effective_message.sticker:
        update.effective_message.reply_text("Please reply with a sticker that belongs to a pack created by me")
        return 0

    # check if the bot has perms to reorder the sticker
    sticker = update.effective_message.sticker
    set_name = sticker.set_name
    if not search(f"{context.bot.username}$", set_name):
        update.effective_message.reply_text("Please reply with a sticker that belongs to a pack created by me")
        return 0

    # get position of sticker in sticker pack
    old_index = new_index = -1
    pack = context.bot.get_sticker_set(set_name)
    for i, s in enumerate(pack.stickers):
        if s.file_id == sticker.file_id:
            new_index = i
        elif s.file_id == reorder[str(update.effective_user.id) + str(update.effective_chat.id)]:
            old_index = i
        if -1 not in (new_index, old_index):
            break

    # get actual new index based on whether sticker is currently before it or after
    if old_index > new_index:
        new_index += 1  # since the empty space will be after the sticker, not before

    # set sticker position
    context.bot.set_sticker_position_in_set(
        reorder[str(update.effective_user.id) + str(update.effective_chat.id)], new_index
    )
    del reorder[str(update.effective_user.id) + str(update.effective_chat.id)]
    update.effective_message.reply_markdown(
        f"I have updated [{context.bot.get_sticker_set(set_name).title}](t.me/addstickers/{set_name})!"
    )

    return ConversationHandler.END


@bot_action("reorder cancel")
def reorder_cancel(update: Update, context: CallbackContext):
    """
    Last step in reordering sticker in pack - take input of sticker which is now gonna be on the left of the reordered sticker
    :param update: object representing the incoming update.
    :param context: object containing data about the bot_action call.
    :return: 0, if wrong input is made, else -1 (ConversationHandler.END)
    """
    # set sticker position
    del reorder[str(update.effective_user.id) + str(update.effective_chat.id)]
    update.effective_message.reply_text(f"Don't wake me up from my nap before you make up your mind!")

    return ConversationHandler.END


__mod_name__ = "Stickers"

__commands__ = [
    CommandDescription(
        command="kang",
        args="<reply> [<emojis>]",
        description=(
            "reply to a sticker (animated or non animated) or a picture to add it to your pack. Won't do anything if "
            "you have an exception set in the chat"
        ),
    ),
    CommandDescription(command="packs", description="list out all of your packs"),
    CommandDescription(
        command="migrate",
        args="<reply>",
        description=(
            "reply to a sticker (animated or non animated) to migrate the entire sticker set it belongs to into your pack(s)"
        ),
    ),
    CommandDescription(
        command="delsticker",
        args="<reply>",
        description="reply to a sticker (animated or non animated) belonging to a pack made by me to remove it from said pack",
    ),
    CommandDescription(
        command="reorder",
        args="<reply>  [<new position>]",
        description=(
            "reply to a sticker (animated or non animated) belonging to a pack made by me to change it's position "
            "(index starting from 0) in the pack"
        ),
    ),
    CommandDescription(
        command="getsticker",
        args="<reply>",
        description="reply to a sticker (non animated) to me to upload its raw PNG file",
    ),
    CommandDescription(
        command="stickerid",
        args="<reply>",
        description="reply to a sticker (animated or non animated) to me to tell you its file ID",
    ),
]

# create handlers
dispatcher.add_handler(CommandHandler("stickerid", sticker_id, run_async=True))
dispatcher.add_handler(CommandHandler("getsticker", get_sticker, run_async=True))
dispatcher.add_handler(CommandHandler("kang", kang, run_async=True))
dispatcher.add_handler(CommandHandler("migrate", migrate, run_async=True))
dispatcher.add_handler(CommandHandler("delsticker", del_sticker, run_async=True))
dispatcher.add_handler(CommandHandler("packs", packs, run_async=True))
dispatcher.add_handler(
    ConversationHandler(
        entry_points=[CommandHandler("reorder", reorder1, run_async=True)],
        states={0: [MessageHandler(Filters.sticker, reorder2, run_async=True)]},
        fallbacks=[CommandHandler("cancel", reorder_cancel, run_async=True)],
    )
)
