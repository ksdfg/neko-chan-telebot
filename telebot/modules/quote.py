from telegram.ext import CommandHandler, run_async, CallbackContext
from telegram import (
    Update,
    UserProfilePhotos,
    Sticker,
)
from telebot import dispatcher
from PIL import ImageFont, ImageDraw, Image, ImageFilter
from os import getcwd, remove
from os.path import join
import glob


def get_sticker(update: Update, context: CallbackContext):
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
        def text_wrap(text, font, max_width):
            lines = []

            # If the width of the text is smaller than image width
            # we don't need to split it, just add it to the lines array
            # and return
            if font.getsize(text)[0] <= max_width:
                lines = text.split("\n")
                print(lines)
                # lines.append(text)
            else:
                # split the line by spaces to get words
                words = text.split(" ")
                i = 0
                # append every word to a line while its width is shorter than image width
                while i < len(words):
                    line = ""
                    while i < len(words) and font.getsize(line + words[i])[0] <= max_width:
                        line = line + words[i] + " "
                        i += 1
                    if not line:
                        line = words[i]
                        i += 1
                    # when the line gets longer than the max width do not append the word,
                    # add the line to the lines array
                    lines.append(line)

            return lines

        def draw_text(name, text):
            max_width = 400
            # img = Image.new("RGB", (400, 120), color=(11, 8, 26))
            # open the background file
            # size() returns a tuple of (width, height)
            # image_size = img.size
            # print(image_size)
            # draw = ImageDraw.Draw(img)
            # create the ImageFont instance
            font_file_path_normal = join(BASE_DIR, "LucidaGrande.ttf")
            font_normal = ImageFont.truetype(font_file_path_normal, size=30, encoding="unic")
            font_file_path_bold = join(BASE_DIR, "LucidaGrandeBold.ttf")
            font_bold = ImageFont.truetype(font_file_path_bold, size=30, encoding="unic")

            # get shorter lines
            lines = text_wrap(text, font_normal, max_width)
            line_height_normal = font_normal.getsize(str(lines[0]))[1]
            line_height_bold = font_bold.getsize(str(name))[1]
            x = 20
            y = 60

            # get scalable weidth and height

            if len(lines) > 1:
                img = Image.new(
                    "RGB",
                    (
                        max_width + 40,
                        70 + (len(lines) * line_height_normal) + line_height_bold,
                    ),
                    color=(11, 8, 26),
                )
                draw = ImageDraw.Draw(img)
                print(lines)
            else:
                line_width_bold = font_bold.getsize(str(name))[0]
                line_width_normal = font_normal.getsize(str(lines[0]))[0]
                img = Image.new(
                    "RGB",
                    (max(line_width_bold, line_width_normal) + 40, 120),
                    color=(11, 8, 26),
                )
                draw = ImageDraw.Draw(img)
                print(lines)

            # get username
            draw.text((20, 25), name, (0, 153, 38), font_bold)
            for line in lines:
                # draw the line on the image
                draw.text((x, y), line, (255, 255, 255), font_normal)
                # update the y position so that we can use it for next line
                y = y + line_height_normal + 5
            # save the image
            img.save(
                f"{update.effective_message.reply_to_message.from_user.id}_text.png",
                optimize=True,
            )
            return img

        def mask_circle_transparent(img, blur_radius, offset=0):
            offset = blur_radius * 2 + offset
            mask = Image.new("L", img.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse(
                (offset, offset, img.size[0] - offset, img.size[1] - offset),
                fill=255,
            )
            mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))

            result = img.copy()
            result.putalpha(mask)

            return result

        def get_ico_thumbnail(dp_name):
            im = Image.open(dp_name)
            size = 100, 100
            result = mask_circle_transparent(im, 0)
            result.thumbnail(size)
            result.save(f"{update.effective_message.reply_to_message.from_user.id}_dp.png")
            return result

        BASE_DIR = getcwd()
        dp = get_ico_thumbnail(f"{update.effective_message.reply_to_message.from_user.id}_dp.jpg")
        body = draw_text(name, text)

    name, text = get_message_data(rep_msg)
    get_raw_sticker(name, text)
    # update.effective_message.reply_text(str(name + "\n" + text + "\n" + profile_pic))
    context.bot.send_sticker(
        chat_id=rep_msg.chat.id,
        sticker=open(f"{update.effective_message.reply_to_message.from_user.id}_text.png", "rb"),
        reply_to_message_id=update.effective_message.message_id,
    )
    context.bot.send_sticker(
        chat_id=rep_msg.chat.id,
        sticker=open(f"{update.effective_message.reply_to_message.from_user.id}_dp.png", "rb"),
        reply_to_message_id=update.effective_message.message_id,
    )
    remove(f"{update.effective_message.reply_to_message.from_user.id}_text.png")
    remove(f"{update.effective_message.reply_to_message.from_user.id}_dp.jpg")


__help__ = """
- /quote : Reply to a message to me to get it's sticker.
"""

__mod_name__ = "quote"

dispatcher.add_handler(CommandHandler('quote', get_sticker))