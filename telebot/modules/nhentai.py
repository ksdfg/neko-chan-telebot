from hentai import Hentai, Format, Tag
from telegram import Update, ParseMode
from telegram.ext import CommandHandler, CallbackContext
from telegram.utils.helpers import escape_markdown
from telegraph import Telegraph

from telebot import dispatcher
from telebot.modules.db.exceptions import get_command_exception_chats
from telebot.utils import bot_action


def _generate_anchor_tags(tags: list[Tag]) -> str:
    """
    Generate comma separated anchor tags for a given list of Tag objects
    :param tags: List of Tag objects
    :return: comma separated anchor tags
    """
    return ", ".join(f'<a href="{tag.url}">{tag.name}</a>' for tag in tags)


@bot_action("sauce")
def sauce(update: Update, context: CallbackContext) -> None:
    """
    Fetch the doujin for all the sauces given by user, make telegraph article and send it to user for easy reading
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    # check if any args were given
    if not context.args:
        update.effective_message.reply_text("Please give some codes to fetch, this cat can't read your mind...")
        return

    # check if exception for sauce is added in current chat
    exception = update.effective_chat.id in get_command_exception_chats("sauce")

    # iterate over each given sauce and fetch the doujin
    for digits in context.args:
        try:
            code = int(digits)
        except ValueError:
            update.effective_message.reply_markdown(
                f"If you don't know that sauce codes must be only digits, you shouldn't be using this command. "
                f"`{digits}` is not a sauce, just a sign of your ignorance."
            )
            continue

        # check if doujin exists
        if not Hentai.exists(code):
            update.effective_message.reply_markdown(
                f"Doujin for `{code}` doesn't exist, Donald... Please don't use your nuclear launch codes here 😿"
            )
            continue

        # Fetch doujin data
        doujin = Hentai(code)

        # get image tags
        image_tags = "\n".join(f'<img src="{image_url}">' for image_url in doujin.image_urls)

        # make dict with data to be displayed for the doujin
        data = {
            "Tags": _generate_anchor_tags(doujin.tag),
            "Characters": _generate_anchor_tags(doujin.character),
            "Parodies": _generate_anchor_tags(doujin.parody),
            "Artists": _generate_anchor_tags(doujin.artist),
            "Groups": _generate_anchor_tags(doujin.group),
            "Languages": _generate_anchor_tags(doujin.language),
            "Categories": _generate_anchor_tags(doujin.category),
        }

        # create telegraph article for the doujin
        telegraph = Telegraph()
        telegraph.create_account(short_name='neko-chan-telebot')
        article_path = telegraph.create_page(doujin.title(Format.Pretty), html_content=image_tags)['path']

        # add details to the reply to be sent to the user
        text_blob = (
            f"<code>{digits}</code>\n<a href='https://telegra.ph/{article_path}'>{doujin.title(Format.Pretty)}</a>"
        )
        for key, value in data.items():
            if value:
                text_blob += f"\n\n<code>{key}</code>\n{value}"

        # send message
        if exception:
            update.message.reply_html(text_blob)
        else:
            context.bot.send_message(chat_id=update.effective_user.id, text=text_blob, parse_mode=ParseMode.HTML)

    # if called from a chat without exception in it, then send him a reminder to check it
    if not exception and update.effective_chat.type != "private":
        update.message.reply_markdown(
            f"[Let's enjoy this together in our private chat...](https://t.me/{escape_markdown(context.bot.username)}"
        )


__help__ = """
- /sauce `<digits list>` : Read a doujin from nhentai.net in telegram instant preview by giving it's code. 
You can give multiple codes, and it will fetch all those doujins. 
If you don't have an exception set for your chat, it'll send it to you in your private chat.
"""

__mod_name__ = "nhentai"

# create handlers
dispatcher.add_handler(CommandHandler('sauce', sauce, run_async=True))
