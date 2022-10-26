from requests import get
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, CommandHandler

from telebot import dispatcher
from telebot.utils import bot_action, CommandDescription, check_command


@bot_action("urban dict")
@check_command("ud")
def ud(update: Update, context: CallbackContext):
    """
    Reply with all the imported modules
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    if context.args:
        try:
            result = get(f'https://api.urbandictionary.com/v0/define?term={" ".join(context.args)}').json()["list"][0]
            update.effective_message.reply_markdown(
                f"***{result['word']}***\n\n{result['definition']}",
                reply_markup=InlineKeyboardMarkup.from_button(
                    InlineKeyboardButton(text="Click here to learn more", url=result["permalink"])
                ),
            )
        except IndexError:
            update.effective_message.reply_markdown(
                "Urban Dictionary doesn't know the answer to this, ask God or offer tuna to a passing cat to gain the "
                "wisdom you seek. Preferably the second option. When I'm passing by."
            )
    else:
        update.effective_message.reply_markdown(
            f"***{update.effective_user.first_name}***\n\n"
            f"A dumbass eternally high on cheap catnip who doesn't know that I can't get a word's "
            f"meaning they don't tell me what the bloody word is.\n\n",
        )


__mod_name__ = "Urban-Dictionary"

__commands__ = (
    CommandDescription(
        command="ud", args="<word>", description="search what the word means according to urban dictionary"
    ),
)

dispatcher.add_handler(CommandHandler("ud", ud, run_async=True))
