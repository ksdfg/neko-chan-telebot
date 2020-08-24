from string import Template

import requests
from bs4 import BeautifulSoup
from telegram import Update, ParseMode
from telegram.ext import CommandHandler, run_async, CallbackContext
from telegraph import Telegraph

from telebot import dispatcher, log
from telebot.modules.sql.exceptions_sql import get_command_exception_chats


def get_info(digits):
    # generate soup object for doujin
    soup = BeautifulSoup(requests.get(f"https://nhentai.net/g/{digits}/").text, 'html.parser')

    title = soup.find('h1').text  # title

    # get gallery ID for the doujin pages
    thumbnail = soup.find("meta", {"itemprop": "image"})
    gallery_id = thumbnail.get('content').split("/")[-2]

    content = soup.find_all("div", {"class": "tag-container"})  # scrape tag container

    parodies = get_content(content, 0)
    characters = get_content(content, 1)
    tags = get_content(content, 2)
    artist = "#" + content[3].find("span", {"class": "name"}).text.replace(' ', '_').replace('-', '_').replace('.', '_')
    groups = get_content(content, 4)
    languages = get_content(content, 5)
    categories = get_content(content, 6)
    pages = content[7].find("span", {"class": "name"}).text

    image_template = Template('<img src="https://i.nhentai.net/galleries/$gallery_id/$page_no.$image_type">')

    image_tags = ""

    for page_no in range(1, int(pages) + 1):
        pg_img = soup.find('a', {'href': f"/g/{digits}/{page_no}/"}).find('img')
        image_type = pg_img.get('data-src').split(".")[-1]
        image_tags += (
            image_template.substitute({'gallery_id': gallery_id, 'page_no': page_no, 'image_type': image_type}) + "\n"
        )

    return (
        title,
        {
            'Tags': tags,
            'Parodies': parodies,
            'Characters': characters,
            'Artists': artist,
            'Groups': groups,
            'Languages': languages,
            'Categories': categories,
        },
        image_tags,
    )


def get_content(content, id):
    info = content[id].find_all("span", {"class": "name"})

    items = []
    for i in range(len(info)):
        items.append(info[i].text)

    if not items:
        return None
    else:
        res = ""
        for item in items:
            res += f"#{item.replace(' ', '_').replace('-', '_').replace('.', '')} "
        return res.strip()


@run_async
def sauce(update: Update, context: CallbackContext):
    log(update, "sauce")

    # check if any args were given
    if not context.args:
        update.effective_message.reply_text("Please give some codes to fetch, this cat can't read your mind...")
        return

    # check if exception for sauce is added in current chat
    exception = update.effective_chat.id in get_command_exception_chats("sauce")

    # iterate over each given sauce and fetch the doujin
    for digits in context.args:
        title, data, image_tags = get_info(digits)

        telegraph = Telegraph()
        telegraph.create_account(short_name='neko-chan-telebot')
        article_path = telegraph.create_page(title, html_content=image_tags)['path']

        text_blob = f"<code>{digits}</code>\n<a href='https://telegra.ph/{article_path}'>{title}</a>"
        for key, value in data.items():
            if value:
                text_blob += f"\n\n<code>{key}</code>\n{value}"

        # send message
        if exception:
            update.message.reply_html(text_blob)
        else:
            context.bot.send_message(chat_id=update.effective_user.id, text=text_blob, parse_mode=ParseMode.HTML)

    if not exception and update.effective_chat.type != "private":
        update.message.reply_markdown(
            f"[Let's enjoy this together in our private chat...](https://t.me/{context.bot.username}"
        )


__help__ = """
- /sauce `<digits list>` : Read a doujin from nhentai.net in telegram instant preview by giving it's 5/6 digit code. 
You can give multiple codes, and it will fetch all those doujins. 
If you don't have an exception set for your chat, it'll send it to you in your private chat.
"""

__mod_name__ = "nhentai"

dispatcher.add_handler(CommandHandler('sauce', sauce))
