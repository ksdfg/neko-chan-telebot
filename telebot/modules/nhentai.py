from os.path import join, dirname

from hentai import Hentai, Format, Tag
from requests.exceptions import RetryError, ConnectionError
from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackContext
from telegraph import Telegraph

from telebot import dispatcher
from telebot.modules.db.exceptions import get_command_exception_chats
from telebot.utils import bot_action, CommandDescription, check_command


def _generate_anchor_tags(tags: list[Tag]) -> str:
    """
    Generate comma separated anchor tags for a given list of Tag objects
    :param tags: List of Tag objects
    :return: comma separated anchor tags
    """
    return ", ".join(f'<a href="{tag.url}">{tag.name}</a>' for tag in tags)


@bot_action("sauce")
@check_command("sauce")
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
        try:
            if not Hentai.exists(code):
                update.effective_message.reply_markdown(
                    f"Doujin for `{code}` doesn't exist, Donald... Please don't use your nuclear launch codes here 😿"
                )
                continue
        except (RetryError, ConnectionError):
            with open(join(dirname(__file__), "assets", "horni_jail.jpg"), "rb") as f:
                update.effective_message.reply_photo(
                    photo=f,
                    caption="Cloudflare won't release any doujins from the horni jail known to most as a browser...",
                    reply_markup=InlineKeyboardMarkup.from_button(
                        InlineKeyboardButton(text="Link to nHentai", url=f"https://nhentai.net/g/{code}")
                    ),
                )
            return

        # Fetch doujin data
        doujin = Hentai(code)

        # get image tags
        image_tags = "\n".join(f'<img src="{image_url}">' for image_url in doujin.image_urls)

        # create telegraph article for the doujin
        telegraph = Telegraph()
        telegraph.create_account(short_name="neko-chan-telebot")
        article_path = telegraph.create_page(doujin.title(Format.Pretty), html_content=image_tags)["path"]

        # make dict with data to be displayed for the doujin
        data = {
            "Code": f'<a href="https://telegra.ph/{article_path}">{code}</a>',
            "Title": f'<a href="{doujin.url}">{doujin.title(Format.Pretty)}</a>',
            "Tags": _generate_anchor_tags(doujin.tag),
            "Pages": f'<a href="https://www.youtube.com/watch?v=dQw4w9WgXcQ">{len(doujin.pages)}</a>',
            "Characters": _generate_anchor_tags(doujin.character),
            "Parodies": _generate_anchor_tags(doujin.parody),
            "Artists": _generate_anchor_tags(doujin.artist),
            "Groups": _generate_anchor_tags(doujin.group),
            "Languages": _generate_anchor_tags(doujin.language),
            "Categories": _generate_anchor_tags(doujin.category),
        }

        # add details to the reply to be sent to the user
        text_blob = "\n\n".join(f"{key}\n{value}" for key, value in data.items() if value)

        # button with nhentai link
        markup = InlineKeyboardMarkup.from_button(InlineKeyboardButton(text="Link to nHentai", url=doujin.url))

        # send message
        if exception:
            update.message.reply_html(text=text_blob, reply_markup=markup)
        else:
            context.bot.send_message(
                chat_id=update.effective_user.id, text=text_blob, parse_mode=ParseMode.HTML, reply_markup=markup
            )

    # if called from a chat without exception in it, then send him a reminder to check it
    if not exception and update.effective_chat.type != "private":
        update.message.reply_text(
            "Let's enjoy this together, without anybody else distracting us...",
            reply_markup=InlineKeyboardMarkup.from_button(
                InlineKeyboardButton(text="Go to Private Chat", url=context.bot.link)
            ),
        )


__mod_name__ = "nhentai"

__commands__ = (
    CommandDescription(
        command="sauce",
        args="<digits list>",
        description=(
            "Read a doujin from nhentai.net in telegram instant preview by giving it's code.\n"
            "You can give multiple codes, and it will fetch all those doujins.\n"
            "If you don't have an exception set for `sauce` in your chat, it'll send it to you in your private chat."
        ),
    ),
)

# create handlers
dispatcher.add_handler(CommandHandler("sauce", sauce, run_async=True))
