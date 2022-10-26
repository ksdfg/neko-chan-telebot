import math
import os
from enum import IntEnum
from os import remove
from pathlib import Path
from re import search
from typing import IO, List
from uuid import uuid4

from PIL import Image
from emoji import emojize
from pydantic import BaseModel
from telegram import (
    Update,
    TelegramError,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Bot,
    User,
    Message,
    StickerSet,
    Sticker,
)
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler, MessageHandler, Filters
from telegram.utils.helpers import escape_markdown

from telebot import dispatcher, config
from telebot.modules.db.exceptions import get_command_exception_chats
from telebot.modules.db.users import add_user
from telebot.utils import bot_action, CommandDescription, check_command


@bot_action("sticker id")
@check_command("stickerid")
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
@check_command("getsticker")
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


class StickerType(IntEnum):
    STATIC = 0
    ANIMATED = 1
    VIDEO = 2


def _generate_pack_name(user: User, bot: Bot, num: int, pack_type: StickerType) -> str:
    """
    Generate a new pack name for given user
    :param user: The user the pack belongs to
    :param bot: The bot that made the pack
    :param num: The pack number for all packs of this type made by bot for user
    :param pack_type: The type of stickers in the pack
    :return: Generated pack name
    """
    name_args: list[str] = [f"a{user.id}"]

    if num > 0:
        name_args.append(str(num))

    match pack_type:
        case StickerType.ANIMATED:
            name_args.append("animated")
        case StickerType.VIDEO:
            name_args.append("video")

    name_args.extend(("by", bot.username))

    return "_".join(name_args)


def _generate_pack_title(user: User, pack_type: StickerType, pack_num: int) -> str:
    """
    Generate a new pack title for given user
    :param user: The user the pack belongs to
    :param pack_type: The type of stickers in the pack
    :param pack_num: Nth pack of this type with user
    :return: Generated pack name
    """
    name_args: list[str] = [f"{user.first_name[:50]}'s"]

    match pack_type:
        case StickerType.ANIMATED:
            name_args.append("animated")
        case StickerType.VIDEO:
            name_args.append("video")

    name_args.append("kang pack")

    if pack_num > 0:
        name_args.append(str(pack_num))

    return " ".join(name_args)


def _get_packs(user: User, bot: Bot, pack_type: StickerType) -> List[StickerSet]:
    """
    get free pack into which we can add stickers
    :param user: the user whose packs we're fetching
    :param bot: the bot to ue to fetch these
    :param pack_type: Type of stickers in the pack
    :return: List of tuples, with each tuple containing the pack number and the pack's StickerSet object
    """
    # list of all the user's packs
    packs: List[StickerSet] = []

    # max number of stickers possible in a pack
    match pack_type:
        case StickerType.ANIMATED:
            max_stickers = 50
        case StickerType.VIDEO:
            max_stickers = 50
        case _:
            max_stickers = 120

    try:
        # default pack number and name of the first pack
        pack_num = 0
        pack_name = _generate_pack_name(user, bot, pack_num, pack_type)
        sticker_set = bot.get_sticker_set(pack_name)
        packs.append(sticker_set)

        while len(sticker_set.stickers) >= max_stickers:
            # since fetched pack is full, get next pack
            try:
                pack_num += 1
                pack_name = _generate_pack_name(user, bot, pack_num, pack_type)
                sticker_set = bot.get_sticker_set(pack_name)
                packs.append(sticker_set)
            except TelegramError:
                # if the next pack doesn't exist yet, then this is the one to use
                break

    except TelegramError:
        # if user hasn't made any pack yet
        pass

    return packs


def _resize(filename: str) -> Image:
    """
    resize an image to fit the required dimensions for a sticker
    :param filename: file name where the image is stored
    :return: Image object of the resized image
    """
    im: Image = Image.open(filename)

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

    im.save(filename)

    return im


def _make_pack(
    msg: Message | None,
    user: User,
    sticker: IO | Path,
    emoji: str,
    bot: Bot,
    pack_name: str,
    pack_num: int,
    pack_type: StickerType,
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
    :param pack_type: Type of the stickers in the pack
    """
    try:
        # create the pack
        pack_title = _generate_pack_title(user, pack_type, pack_num)
        match pack_type:
            case StickerType.STATIC:
                bot.create_new_sticker_set(user.id, pack_name, pack_title, png_sticker=sticker, emojis=emoji)
            case StickerType.ANIMATED:
                bot.create_new_sticker_set(user.id, pack_name, pack_title, png_sticker=sticker, emojis=emoji)
            case StickerType.VIDEO:
                bot.create_new_sticker_set(user.id, pack_name, pack_title, webm_sticker=sticker, emojis=emoji)

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

            case _:
                raise e

        return

    # send result to user
    if msg:
        msg.reply_markdown(f"Sticker pack successfully created. Get it [here](t.me/addstickers/{pack_name}).")
    print(f"created pack {pack_name}")


class MessageContentException(Exception):
    pass


class CustomSticker(BaseModel):
    type: StickerType | None
    content: str | Path | IO | None
    emoji: str = "🤔"

    bot: Bot
    user: User

    class Config:
        arbitrary_types_allowed = True

    def _get_temp_file_name(self) -> str:
        """
        :return: filename for temporarily downloading content in order to process it
        """
        extension: str = ""
        match self.type:
            case StickerType.STATIC:
                extension = "png"
            case StickerType.ANIMATED:
                extension = "tgs"
            case StickerType.VIDEO:
                extension = "webm"

        return f"/tmp/{self.user.id}_{uuid4()}_kang_sticker.{extension}"

    def extract_from_sticker(self, sticker: Sticker) -> None:
        """
        Extract all details of a sticker into current custom sticker
        :param sticker: The sticker to be copied
        :return: nothing
        """
        self.emoji = sticker.emoji

        if sticker.is_animated:
            self.type = StickerType.ANIMATED
            filename = self._get_temp_file_name()
            sticker.get_file().download(filename)
            self.content = open(filename, "rb")

        elif sticker.is_video:
            self.type = StickerType.VIDEO
            filename = self._get_temp_file_name()
            sticker.get_file().download(filename)
            self.content = open(filename, "rb")

        else:
            self.type = StickerType.STATIC
            self.content = sticker.file_id

    def extract_from_msg(self, msg: Message) -> None:
        """
        Extract all details required for the sticker from the message user replied to
        :param msg: The message user sent to the bot
        :return: nothing
        """
        content_msg: Message = msg.reply_to_message
        if not content_msg:
            raise MessageContentException

        # if msg is a sticker, then copy all details from it
        if content_msg.sticker:
            self.extract_from_sticker(content_msg.sticker)

        # if msg is a photo, get file ID of the largest resolution of the image and resize
        elif content_msg.photo:
            self.type = StickerType.STATIC

            filename = self._get_temp_file_name()
            self.bot.get_file(msg.reply_to_message.photo[-1].file_id).download(filename)
            _resize(filename)
            self.content = Path(filename)

        # if msg is a document, get file ID of the doc and resize it
        elif content_msg.document:
            self.type = StickerType.STATIC

            filename = self._get_temp_file_name()
            self.bot.get_file(msg.reply_to_message.document.file_id).download(filename)
            _resize(filename)
            self.content = Path(filename)

        else:
            raise MessageContentException

    def add_to_pack(self, pack: StickerSet) -> None:
        """
        Add a sticker to a pack
        :param pack: The sticker set to add the sticker to
        :return: nothing
        """
        match self.type:
            case StickerType.STATIC:
                self.bot.add_sticker_to_set(
                    user_id=self.user.id, name=pack.name, png_sticker=self.content, emojis=self.emoji
                )

            case StickerType.ANIMATED:
                self.bot.add_sticker_to_set(
                    user_id=self.user.id, name=pack.name, tgs_sticker=open(self.content, "rb"), emojis=self.emoji
                )

            case StickerType.VIDEO:
                self.bot.add_sticker_to_set(
                    user_id=self.user.id, name=pack.name, webm_sticker=self.content, emojis=self.emoji
                )

    def delete_kang_temp_files(self) -> None:
        """
        Delete all temp files created while kanging a sticker
        :return: nothing
        """
        file_name = self._get_temp_file_name()
        if os.path.isfile(file_name):
            os.remove(file_name)


@bot_action("kang")
@check_command("kang")
def kang(update: Update, context: CallbackContext) -> None:
    """
    Add a sticker to user's pack
    :param update: object representing the incoming update
    :param context: object containing data about the bot_action call
    """
    # check for exception, but skip exception if user is a superuser
    if update.effective_user.id not in config.SUPERUSERS and update.effective_chat.id in get_command_exception_chats(
        "kang"
    ):
        return

    msg = update.effective_message
    user = update.effective_user
    bot = context.bot

    # get sticker details from message
    sticker = CustomSticker(bot=bot, user=user)
    try:
        sticker.extract_from_msg(msg)
    except MessageContentException:
        msg.reply_text("I can only kang images, tgs files and webm files.\n\n\nAnd catnip. If I'm feeling like it.")

    # override emoji if sent in message
    if context.args:
        sticker.emoji = context.args[0]

    # get sticker pack of user
    packs = _get_packs(user, bot, sticker.type)

    # if packs exist, add sticker to last pack in list
    if packs:
        pack = packs[-1]
        pack_name = pack.name
        pack_title = pack.title

        try:
            sticker.add_to_pack(pack)

        except OSError:
            msg.reply_text("I can only kang images.\nAnd catnip. If I'm feeling like it.")
            return

        except TelegramError as e:
            match e.message:
                case "Invalid sticker emojis":
                    msg.reply_text("Invalid emoji(s).")

                case "Stickers_too_much":
                    msg.reply_text("Meowtastic news! This loser just maxed out his pack size. Press F to pay respecc.")

                case _:
                    raise e

        msg.reply_markdown(
            f"Sticker successfully added to [{pack_title}](t.me/addstickers/{pack_name})\nEmoji is : {sticker.emoji}"
        )

    # if no packs exist, make a new pack with the sticker
    else:
        pack_name = _generate_pack_name(user, bot, 0, sticker.type)
        pack_title = _generate_pack_title(user, sticker.type, 0)

        _make_pack(msg, user, sticker.content, sticker.emoji, bot, pack_name, 0, sticker.type)

    sticker.delete_kang_temp_files()


@bot_action("migrate pack")
@check_command("migrate")
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

    # Get orignal set's sticker metadata
    if not og_stickers_set.stickers:
        update.effective_message.reply_text("Congratulations on finding a sticker pack with no stickers...")
    custom_sticker = CustomSticker(user=update.effective_user, bot=context.bot)
    custom_sticker.extract_from_sticker(stickers[0])
    pack_type = custom_sticker.type

    # get the pack to migrate the stickers into
    packs = _get_packs(update.effective_user, context.bot, pack_type)
    if packs:
        sticker_pack = packs[-1]
        pack_name = sticker_pack.name
        pack_num = len(packs) - 1
    else:
        # generate new pack
        pack_num = 0
        pack_name = _generate_pack_name(update.effective_user, context.bot, pack_num, stickers[0].type)
        _make_pack(
            None,
            update.effective_user,
            stickers[0].content,
            stickers[0].emoji,
            context.bot,
            pack_name,
            pack_num,
            pack_type,
        )

        # remove first sticker from list of stickers to migrate
        stickers = stickers[1:]

        sticker_pack = context.bot.get_sticker_set(pack_name)

    appended_packs = [sticker_pack]  # list of packs the stickers were migrated into

    match pack_type:
        case StickerType.ANIMATED:
            max_stickers = 50
        case StickerType.VIDEO:
            max_stickers = 50
        case _:
            max_stickers = 120

    for sticker in stickers:
        # Extract sticker data
        custom_sticker = CustomSticker(user=update.effective_user, bot=context.bot)
        custom_sticker.extract_from_sticker(sticker)

        # if current pack can still fit in more stickers
        if len(sticker_pack.stickers) < max_stickers:
            try:
                custom_sticker.add_to_pack(sticker_pack)

            except OSError:
                continue

            except TelegramError as e:
                match e.message:
                    case "Stickers_too_much":
                        print(len(sticker_pack.stickers))

            # update sticker pack
            sticker_pack = context.bot.get_sticker_set(pack_name)

        # if current pack is full
        else:
            # generate new pack
            pack_num += 1
            pack_name = _generate_pack_name(update.effective_user, context.bot, pack_num, pack_type)
            _make_pack(
                None,
                update.effective_user,
                custom_sticker.content,
                custom_sticker.emoji,
                context.bot,
                pack_name,
                pack_num,
                pack_type,
            )

            sticker_pack = context.bot.get_sticker_set(pack_name)
            appended_packs.append(sticker_pack)

        custom_sticker.delete_kang_temp_files()

    # send success reply to the user
    reply = "\n".join(
        (
            f"Done! Pack [{og_set_title}](t.me/addstickers/{og_set_name}) was migrated into :-",
            *[f"[{pack.title}](t.me/addstickers/{pack.name})" for pack in appended_packs],
        )
    )
    update.effective_message.reply_markdown(reply)


@bot_action("delete sticker")
@check_command("delsticker")
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
@check_command("packs")
def packs(update: Update, context: CallbackContext):
    """
    List all the packs of a user
    :param update: object representing the incoming update.
    :param context: object containing data about the bot_action call.
    """
    # get all user packs
    packs = (
        _get_packs(update.effective_user, context.bot, StickerType.STATIC)
        + _get_packs(update.effective_user, context.bot, StickerType.ANIMATED)
        + _get_packs(update.effective_user, context.bot, StickerType.VIDEO)
    )

    if packs:
        reply = "Here's all your meowtastic packs!\n"
        for pack in packs:
            reply += f"\n[{pack.title}](t.me/addstickers/{pack.name})"

        update.effective_message.reply_markdown(reply)

    else:
        update.effective_message.reply_text(
            emojize("You have no packs yet! kang or migrate to make one :grinning_cat_face_with_smiling_eyes:")
        )


# dict of user - sticker to reorder
reorder = {}


@bot_action("reorder step 1")
@check_command("reorder")
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
    user_chat = reorder[str(update.effective_user.id) + str(update.effective_chat.id)]
    for i, s in enumerate(pack.stickers):
        if s.file_id == sticker.file_id:
            new_index = i
        elif s.file_id == user_chat:
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
@check_command("cancel")
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

__commands__ = (
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
        description="reply to a sticker (animated or non animated) belonging to a pack made by me to remove it from "
                    "said pack",
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
)

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
