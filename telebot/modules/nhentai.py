from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, run_async
from string import Template
import requests
from bs4 import BeautifulSoup
from telegraph import Telegraph
from telebot import dispatcher, log


def get_info(soup):
    title = soup.find('h1').text  # title
    title_jap = soup.find('h2').text  # title in japnese
    article = soup.find("h3", {"id": "gallery_id"}).text  # hash id

    thumbnail = soup.find("meta", {"itemprop": "image"})
    gallery_id = thumbnail.get('content').split("/")[-2]

    content = soup.find_all("div", {"class": "tag-container"})  # scrape tag container

    parodies = get_content(content, 0)
    characters = get_content(content, 1)
    tags = get_content(content, 2)
    artist = get_content(content, 3)
    groups = get_content(content, 4)
    languages = get_content(content, 5)
    categories = get_content(content, 6)
    pages = get_content(content, 7)

    image_template = Template('<img src="https://i.nhentai.net/galleries/$gallery_id/$page_no.jpg">')

    image_tags = ""

    for page_no in range(1, int(pages.replace("#", ""))):
        image_tags += image_template.substitute({'gallery_id': gallery_id, 'page_no': page_no}) + "\n"

    return title, title_jap, article, parodies, characters, tags, artist, groups, languages, categories, image_tags


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
            res += f"#{item.replace(' ', '_').replace('-', '_')} "
        return res.strip()


def run(sauce):
    url = f"https://nhentai.net/g/{sauce}/"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    (
    title,
    title_jap,
    article,
    parodies,
    characters,
    tags,
    artist,
    groups,
    languages,
    categories,
    image_tags,
    ) = get_info(soup)
    telegraph = Telegraph()

    telegraph.create_account(short_name='1337')

    response = telegraph.create_page(str(title), html_content=image_tags,)
    message = 'https://telegra.ph/{}'.format(response['path']) + "\n" + "title: " + str(title) + "\n" + "title_jap: " + str(title_jap) + "\n" + "article: " + str(article) + "\n" + "parodies: " + str(parodies) + "\n" + "characters: " + str(characters) + "\n" + "tags: " + str(tags) + "\n" + "artist: " + str(artist) + "\n" + "groups: " + str(groups) + "\n" + "languages: " + str(languages) + "\n" + "categories: " + str(categories)
    return message



@run_async
def sauce(update, context):
    text = context.args
    for i in range(0, len(text)):
        message = run(text[i])
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)

__help__ = """
- /sauce: Give 6 Digit number for hentai on nhentai.net
"""
__mod_name__ = "nhentai"

dispatcher.add_handler(CommandHandler('sauce', sauce))

