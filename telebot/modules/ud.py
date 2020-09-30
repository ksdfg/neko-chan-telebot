from requests import get
from telegram import Update
from telegram.ext import run_async, CallbackContext, CommandHandler

from telebot import dispatcher
from telebot.functions import bot_action


@run_async
@bot_action("urban dict")
def ud(update: Update, context: CallbackContext):
    """
    Reply with all the imported modules
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    results = get(f'http://api.urbandictionary.com/v0/define?term={" ".join(context.args)}').json()
    reply_text = (
        (
            f"***Word***: {' '.join(context.args)}\n\n"
            f"***Definition***:\n{results['list'][0]['definition']}\n\n"
            f"[Click here to learn more]({results['list'][0]['permalink']})"
        )
        if results.get('list')
        else (
            "Urban Dictionary doesn't know the answer to this, "
            "ask God or offer tuna to a passing cat to gain the wisdom you seek. "
            "Preferably the second option. When I'm passing by."
        )
    )
    update.effective_message.reply_markdown(reply_text, disable_web_page_preview=True)


__help__ = """
 - /ud `<word>`: Type the word or expression you want to search use.
 """

__mod_name__ = "Urban-Dictionary"

dispatcher.add_handler(CommandHandler("ud", ud))
