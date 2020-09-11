import random
from os import remove
from os.path import join
from pathlib import Path

from PIL import ImageFont, ImageDraw, Image, ImageFilter
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

from telebot import dispatcher


def get_sticker(update: Update, context: CallbackContext):
    context.bot.send_chat_action(update.effective_chat.id, 'upload_photo')
    rep_msg = update.effective_message.reply_to_message

    def generate_temp_profile(name, assigned_color):
        BASE_DIR = Path(__file__).parent.absolute()
        ls = name.split(" ")
        if len(ls) > 1:
            initials = ls[0][0] + ls[1][0]
        else:
            initials = ls[0][0]

        font_bold = ImageFont.truetype(join(BASE_DIR, 'Fonts', "LucidaGrandeBold.ttf"), size=60, encoding="unic")
        img = Image.new("RGB", (160, 160), color=(assigned_color))
        draw = ImageDraw.Draw(img)
        text_width, text_height = draw.textsize(initials, font_bold)
        position = ((160 - text_width) / 2, (160 - text_height) / 2)
        draw.text(position, initials, (255, 255, 255), font=font_bold)
        img.save(
            f"{update.effective_message.reply_to_message.from_user.id}_dp.jpg",
        )

    def get_message_data(rep_msg):  # Get required data of the message to be quoted

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

        if rep_msg.from_user.last_name:
            name = rep_msg.from_user.first_name + " " + rep_msg.from_user.last_name
        else:
            name = rep_msg.from_user.first_name

        text = ""

        if rep_msg.text:
            text = rep_msg.text

        try:
            profile_pic = update.effective_message.reply_to_message.from_user.get_profile_photos().photos[0][
                0
            ]  # Get users Profile Photo

            file_pp = context.bot.getFile(profile_pic)
            file_pp.download(f"{update.effective_message.reply_to_message.from_user.id}_dp.jpg")

        except IndexError:
            generate_temp_profile(name, assigned_color)

        return name, text, assigned_color

    def get_raw_sticker(name, text, assigned_color):
        def text_wrap(text: str, font: ImageFont, max_width: int) -> str:
            """
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

        def add_corners(img):
            rad = 30
            circle = Image.new("L", (rad * 2, rad * 2), 0)
            draw = ImageDraw.Draw(circle)
            draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
            alpha = Image.new("L", img.size, 255)
            w, h = img.size
            alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
            alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
            alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
            alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
            img.putalpha(alpha)
            return img

        def draw_text(name, text, assigned_color):
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

            result = add_corners(img)

            return result

        def mask_circle_transparent(img, offset=0):
            # mask the background of circular profile pic thumbnail
            offset = 0 * 2 + offset
            mask = Image.new("L", img.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse(
                (offset, offset, img.size[0] - offset, img.size[1] - offset),
                fill=255,
            )
            mask = mask.filter(ImageFilter.GaussianBlur(0))

            result = img.copy()
            result.putalpha(mask)

            return result

        def get_ico_thumbnail(dp_name):
            # get circular profile pic
            im = Image.open(dp_name)
            size = 100, 100
            result = mask_circle_transparent(im)
            result.thumbnail(size)
            return result

        def get_concat_h(img1, img2):
            # concat both images
            dst = Image.new("RGB", (img1.width + img2.width + 15, max(img1.height, img2.height)))
            dst.putalpha(0)
            dst.paste(img1, (0, 0))
            dst.paste(img2, (img1.width + 15, 0))
            basewidth = 512
            wpercent = basewidth / float(dst.size[0])
            hsize = int((float(dst.size[1]) * float(wpercent)))
            dst = dst.resize((basewidth, hsize), Image.ANTIALIAS)
            # save image in webp format
            dst.save(
                f"{update.effective_message.reply_to_message.from_user.id}_final.png",
                "PNG",
                lossless=True,
            )

        # get base directory
        BASE_DIR = Path(__file__).parent.absolute()
        dp = get_ico_thumbnail(f"{update.effective_message.reply_to_message.from_user.id}_dp.jpg")
        body = draw_text(name, text, assigned_color)
        get_concat_h(dp, body)

    try:
        name, text, assigned_color = get_message_data(rep_msg)
        get_raw_sticker(name, text, assigned_color)

        # send generated image as sticker
        rep_msg.reply_sticker(sticker=open(f"{update.effective_message.reply_to_message.from_user.id}_final.png", "rb"))

        # remove stored images
        remove(f"{update.effective_message.reply_to_message.from_user.id}_final.png")
        remove(f"{update.effective_message.reply_to_message.from_user.id}_dp.jpg")

    except AttributeError:
        update.effective_message.reply_text(
            "Please reply to a message to get its quote.\nThis cat can't read your mind"
        )


__help__ = """
- /quote : Reply to a message to me to get it's sticker.
"""

__mod_name__ = "quote"

dispatcher.add_handler(CommandHandler('quote', get_sticker))
