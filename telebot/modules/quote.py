import random
from os import remove
from os.path import join, isfile
from pathlib import Path
from typing import Tuple
from uuid import uuid4

from PIL import ImageFont, ImageDraw, Image, ImageFilter
from telegram import Update, Message
from telegram.ext import CommandHandler, CallbackContext, run_async

from telebot import dispatcher
from telebot.functions import log


def _message_to_sticker(update: Update, context: CallbackContext) -> str:
    """
    Function to make the sticker from message and save it on disk as png image
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    :return: name of file on disk
    """
    rep_msg = update.effective_message.reply_to_message

    file_name = f"{update.effective_message.reply_to_message.from_user.id}_{uuid4()}"

    def generate_temp_profile(name, assigned_color):
        """
        generate temporary profile picture
        :param name: username
        :param assigned_color: random color assigned to user similar to telegram
        """
        # Fetch Initials of full name
        BASE_DIR = Path(__file__).parent.absolute()
        ls = name.split(" ")
        if len(ls) > 1:
            initials = ls[0][0] + ls[1][0]
        else:
            initials = ls[0][0]
        # Generate a temp profile picture similar to telegram
        font_bold = ImageFont.truetype(join(BASE_DIR, 'Fonts', "LucidaGrandeBold.ttf"), size=60, encoding="unic")
        img = Image.new("RGB", (160, 160), color=(assigned_color))
        draw = ImageDraw.Draw(img)
        # put the initials in centre of image
        text_width, text_height = draw.textsize(initials, font_bold)
        position = ((160 - text_width) / 2, (160 - text_height) / 2)
        draw.text(position, initials, (255, 255, 255), font=font_bold)
        # save the image
        img.save(
            f"{file_name}_dp.jpg",
        )

    def get_message_data(rep_msg: Message) -> Tuple[str, str, Tuple[int, int, int]]:
        """
        Get required data of the message to be quoted
        :param rep_msg: object representing replied message information
        :return: name of user, message to be quoted and assigned color
        """
        # List consisting tuples of RGB for random color generation similar to telegram
        head_tg = [
            (238, 73, 40),
            (65, 169, 3),
            (224, 150, 2),
            (15, 148, 237),
            (143, 59, 247),
            (252, 67, 128),
            (0, 161, 196),
            (235, 112, 2),
        ]
        assigned_color = random.choice(head_tg)

        # Get Name and message quote

        if rep_msg.from_user.last_name:
            name = rep_msg.from_user.first_name + " " + rep_msg.from_user.last_name
        else:
            name = rep_msg.from_user.first_name

        text = ""

        if rep_msg.text:
            text = rep_msg.text

        try:
            # Get users Profile Photo
            profile_pic = update.effective_message.reply_to_message.from_user.get_profile_photos().photos[0][0]

            file_pp = context.bot.getFile(profile_pic)
            file_pp.download(f"{file_name}_dp.jpg")

        except IndexError:
            generate_temp_profile(name, assigned_color)

        return name, text, assigned_color

    def get_raw_sticker(name: str, text: str, assigned_color: Tuple[int, int, int]):
        """
        :param name: Username of the quoted message
        :param text: Message info to be quoted
        :param assigned_color: random color assigned to the user similar to telegram
        """

        def text_wrap(text: str, font: ImageFont, max_width: int) -> str:
            """
            Function to determine the number of lines the text is divided in.
            Get properly formatted text
            :param text: The base message text
            :param font: font to be used for the format
            :param max_width: maximum width of the rendered text
            :return: The formatted text as a string
            """
            text_blob = ""

            for line in text.split("\n"):
                # for each line
                line_text = ""
                for word in line.split(" "):
                    if font.getsize(line_text + word)[0] > max_width:
                        # append current line to the text_blob, and shift current word to next line
                        text_blob += line_text.strip() + "\n"
                        line_text = word
                    else:
                        # append current word to the line
                        line_text += " " + word

                # append current line to the text blob
                text_blob += line_text.strip() + "\n"

            return text_blob.strip()

        def add_corners(img: Image) -> Image:
            """
            apply rounded corners
            :param img: Generated image
            :return: Rounded corner image
            """
            rad = 30
            # generate new circular image
            circle = Image.new("L", (rad * 2, rad * 2), 0)
            draw = ImageDraw.Draw(circle)
            draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
            alpha = Image.new("L", img.size, 255)
            w, h = img.size
            # determine the rounded radius and edit image accordingly to all corners
            alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
            alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
            alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
            alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
            img.putalpha(alpha)
            return img

        def draw_text(name: str, text: str, assigned_color: Tuple[int, int, int]) -> Image:
            """
            create raw image for text
            :param name: Name of user
            :param text: Message to be quoted
            :param assigned_color: random color assigned to the user similar to telegram
            :return: raw image consisting of quoted text
            """
            max_width = 400

            # create the ImageFont instances
            font_normal = ImageFont.truetype(join(BASE_DIR, 'Fonts', "LucidaGrande.ttf"), size=30, encoding="unic")
            font_bold = ImageFont.truetype(join(BASE_DIR, 'Fonts', "LucidaGrandeBold.ttf"), size=30, encoding="unic")

            # get text_blob
            text_blob = text_wrap(text, font_normal, max_width)

            # get width and height of name and text blob
            line_width_bold, line_height_bold = font_bold.getsize(name)
            line_width, line_height = font_normal.getsize_multiline(text_blob)

            # get scalable width and height
            img = Image.new(
                "RGB",
                (
                    max(line_width_bold, line_width) + 40,
                    25 + line_height_bold + 45 + line_height + 25,
                ),
                color=(11, 8, 26),
            )
            draw = ImageDraw.Draw(img)

            # put username
            draw.text((20, 25), name, assigned_color, font_bold)

            # put text
            draw.multiline_text((20, 15 + line_height_bold + 45), text_blob, (255, 255, 255), font_normal)

            # add rounded corners
            result = add_corners(img)

            return result

        def mask_circle_transparent(img: Image, offset: int = 0) -> Image:
            """
            mask the background of circular profile pic thumbnail
            :param img: Profile picture to convert to circular shape
            :param offset: determining the shape of image
            :return: circular and transparent background profile picture
            """
            offset = 0 * 2 + offset
            mask = Image.new("L", img.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse(
                (offset, offset, img.size[0] - offset, img.size[1] - offset),
                fill=255,
            )
            # apply transparency to background
            mask = mask.filter(ImageFilter.GaussianBlur(0))

            result = img.copy()
            result.putalpha(mask)

            return result

        def get_ico_thumbnail(dp_name: str) -> Image:
            """
            get circular profile pic
            :param dp_name: rectangular 160x160 profile picture
            :return: circular profile picture thumbnail
            """
            im = Image.open(dp_name)
            size = 100, 100
            result = mask_circle_transparent(im)
            result.thumbnail(size)
            return result

        def get_concat_h(img1: Image, img2: Image):
            """
            join 2 images to create a quoted image similar to telegram
            :param img1: Circular profile picture thumbnail
            :param img2: Image consisting text message and name of the user
            """
            # concat both images
            dst = Image.new("RGB", (img1.width + img2.width + 15, max(img1.height, img2.height)))
            dst.putalpha(0)
            dst.paste(img1, (0, 0))
            dst.paste(img2, (img1.width + 15, 0))
            # rebase image to fit into telegram's sticker's dimension rules
            basewidth = 512
            wpercent = basewidth / float(dst.size[0])
            hsize = int((float(dst.size[1]) * float(wpercent)))
            dst = dst.resize((basewidth, hsize), Image.ANTIALIAS)
            # save image in png format
            dst.save(
                f"{file_name}_final.png",
                "PNG",
                lossless=True,
            )

        # get base directory
        BASE_DIR = Path(__file__).parent.absolute()

        # make sticker
        dp = get_ico_thumbnail(f"{file_name}_dp.jpg")
        body = draw_text(name, text, assigned_color)
        get_concat_h(dp, body)

    # get message data and use it to generate sticker
    name, text, assigned_color = get_message_data(rep_msg)
    get_raw_sticker(name, text, assigned_color)

    # delete saved profile picture from local storage
    if isfile(f"{file_name}_dp.jpg"):
        remove(f"{file_name}_dp.jpg")

    return f"{file_name}_final.png"


@run_async
def quote(update: Update, context: CallbackContext):
    """
    convert message into quote and reply
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    log(update, "quote")

    context.bot.send_chat_action(update.effective_chat.id, 'upload_photo')  # tell chat that a sticker is incoming

    # make sticker and save on disk
    try:
        file_name = _message_to_sticker(update, context)
    except AttributeError:
        update.effective_message.reply_text(
            "Please reply to a message to get its quote.\nThis cat can't read your mind"
        )
        return

    # send generated image as sticker
    update.effective_message.reply_sticker(sticker=open(file_name, "rb"))

    # remove stored image
    # if isfile(file_name):
    #     remove(file_name)


__help__ = """
- /quote `<reply>` : Reply to a message to get it's quote as a sticker.
"""

__mod_name__ = "quote"

dispatcher.add_handler(CommandHandler('quote', quote))
