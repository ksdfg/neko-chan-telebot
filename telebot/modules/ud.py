from random import choice

from requests import get
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, CommandHandler

from telebot import dispatcher
from telebot.utils import bot_action


@bot_action("urban dict")
def ud(update: Update, context: CallbackContext):
    """
    Reply with all the imported modules
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    if context.args:
        try:
            result = choice(
                get(f'http://api.urbandictionary.com/v0/define?term={" ".join(context.args)}').json()["list"]
            )
            update.effective_message.reply_markdown(
                f"***Word***: {' '.join(context.args)}\n\n***Definition***:\n{result['definition']}\n\n",
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="Click here to learn more", url=result["permalink"])]]
                ),
            )
        except IndexError:
            update.effective_message.reply_markdown(
                "Urban Dictionary doesn't know the answer to this, ask God or offer tuna to a passing cat to gain the "
                "wisdom you seek. Preferably the second option. When I'm passing by."
            )
    else:
        update.effective_message.reply_markdown(
            f"***Word***: {update.effective_user.first_name}\n\n"
            f"***Definition***:\nA dumbass eternally high on cheap catnip who doesn't know that I can't get a word's "
            f"meaning they don't tell me what the bloody word is.\n\n",
        )


__help__ = """
 - /ud `<word>`: Type the word or expression you want to search use.
 """

__mod_name__ = "Urban-Dictionary"

dispatcher.add_handler(CommandHandler("ud", ud, run_async=True))
