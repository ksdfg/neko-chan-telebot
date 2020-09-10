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

    def get_message_data(rep_msg):  # Get required data of the message to be quoted

        profile_pic = update.effective_message.reply_to_message.from_user.get_profile_photos().photos[0][
            0
        ]  # Get users Profile Photo

        file_pp = context.bot.getFile(profile_pic)
        file_pp.download(f"{update.effective_message.reply_to_message.from_user.id}_dp.jpg")

        if rep_msg.from_user.last_name:
            name = rep_msg.from_user.first_name + " " + rep_msg.from_user.last_name
        else:
            name = rep_msg.from_user.first_name

        text = ""

        if rep_msg.text:
            text = rep_msg.text

        return name, text

    def get_raw_sticker(name, text):
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

        def draw_text(name, text):
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
            draw.text((20, 25), name, (0, 153, 38), font_bold)

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
            # save image in webp format
            dst.save(
                f"{update.effective_message.reply_to_message.from_user.id}_final.webp",
                "WEBP",
                lossless=True,
            )

        # get base directory
        BASE_DIR = Path(__file__).parent.absolute()
        dp = get_ico_thumbnail(f"{update.effective_message.reply_to_message.from_user.id}_dp.jpg")
        body = draw_text(name, text)
        get_concat_h(dp, body)

    name, text = get_message_data(rep_msg)
    get_raw_sticker(name, text)

    # send generated image as sticker
    rep_msg.reply_sticker(sticker=open(f"{update.effective_message.reply_to_message.from_user.id}_final.webp", "rb"))

    # remove stored images
    remove(f"{update.effective_message.reply_to_message.from_user.id}_final.webp")
    remove(f"{update.effective_message.reply_to_message.from_user.id}_dp.jpg")


__help__ = """
- /quote : Reply to a message to me to get it's sticker.
"""

__mod_name__ = "quote"

dispatcher.add_handler(CommandHandler('quote', get_sticker))
