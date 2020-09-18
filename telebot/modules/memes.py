from random import choice, randint
from re import sub

from spongemock.spongemock import mock as mock_text
from telegram import Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler, run_async
from telegram.utils.helpers import escape_markdown
from zalgo_text.zalgo import zalgo

from telebot import dispatcher
from telebot.functions import bot_action


@run_async
@bot_action("runs")
def runs(update: Update, context: CallbackContext) -> None:
    """
    Insulting reply whenever someone uses /runs
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    update.effective_message.reply_markdown("I'm a cute kitty, and here we have a fat pussy.")
    update.effective_chat.send_sticker("CAACAgUAAxkBAAIJK19CjPoyyX9QwwHfNOZMnqww1hxXAALfAAPd6BozJDBFCIENpGkbBA")


@run_async
@bot_action("mock")
def mock(update: Update, context: CallbackContext) -> None:
    """
    Mock a message like spongebob, and reply
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    if update.effective_message.reply_to_message:
        update.effective_message.reply_to_message.reply_text(mock_text(update.effective_message.reply_to_message.text))
    else:
        update.effective_message.reply_text("I don't see anything to mock here other than your ugly face...")


@run_async
@bot_action("zalgofy")
def zalgofy(update: Update, context: CallbackContext) -> None:
    """
    Corrupt the way the text looks, and reply
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    if update.effective_message.reply_to_message:
        update.effective_message.reply_to_message.reply_text(
            zalgo().zalgofy(update.effective_message.reply_to_message.text)
        )
    else:
        update.effective_message.reply_text("Gimme a message to zalgofy before I claw your tits off...")


@run_async
@bot_action("owo")
def owo(update: Update, context: CallbackContext) -> None:
    """
    Change a message to look like it was said by a moe weeb
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    if not update.effective_message.reply_to_message:
        update.effective_message.reply_text(
            "Gommenye, I don't nyaruhodo what normie text you want to henshin into the moe weeb dialect"
        )
        return

    # list of all kaomojis to use in owo
    kaomoji = [
        escape_markdown("```\n(・`ω´・)\n```"),
        escape_markdown("```\n;;w;;\n```"),
        escape_markdown("```\nowo\n```"),
        escape_markdown("```\nUwU\n```"),
        escape_markdown("```\n>w<\n```"),
        escape_markdown("```\n^w^\n```"),
        escape_markdown("```\n" + r"\(^o\) (/o^)/" + "\n```"),
        escape_markdown("```\n( ^ _ ^)∠☆\n```"),
        escape_markdown("```\n(ô_ô)\n```"),
        escape_markdown("```\n~:o\n```"),
        escape_markdown("```\n;____;\n```"),
        escape_markdown("```\n(*^*)\n```"),
        escape_markdown("```\n(>_\n```"),
        escape_markdown("```\n(♥_♥)\n```"),
        escape_markdown("```\n*(^O^)*\n```"),
        escape_markdown("```\n((+_+))\n```"),
    ]

    try:
        # replace certain characters and add a kaomoji
        reply_text = sub(r'[rl]', "w", update.effective_message.reply_to_message.text_markdown)
        reply_text = sub(r'[ｒｌ]', "ｗ", reply_text)
        reply_text = sub(r'[RL]', 'W', reply_text)
        reply_text = sub(r'[ＲＬ]', 'Ｗ', reply_text)
        reply_text = sub(r'n([aeiouａｅｉｏｕ])', r'ny\1', reply_text)
        reply_text = sub(r'ｎ([ａｅｉｏｕ])', r'ｎｙ\1', reply_text)
        reply_text = sub(r'N([aeiouAEIOU])', r'Ny\1', reply_text)
        reply_text = sub(r'Ｎ([ａｅｉｏｕＡＥＩＯＵ])', r'Ｎｙ\1', reply_text)
        reply_text = sub(r'!+', ' ' + choice(kaomoji), reply_text)
        reply_text = sub(r'！+', ' ' + choice(kaomoji), reply_text)
        reply_text = reply_text.replace("ove", "uv")
        reply_text = reply_text.replace("ｏｖｅ", "ｕｖ")
        reply_text += "\n" + choice(kaomoji)

        # reply to the original message
        update.effective_message.reply_to_message.reply_markdown(reply_text)

    except BadRequest:
        # in case we messed up markdown while replacing characters and adding kaomoji
        update.effective_message.reply_text(
            "Gommenye, I over-owo'd myself.... please try again. "
            "If it still doesn't work, then this must be the language of god's you're trying to translate...."
        )


@run_async
@bot_action("stretch")
def stretch(update: Update, context: CallbackContext):
    """
    Stretch the vowels in a message by a random count
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    if not update.effective_message.reply_to_message:
        update.effective_message.reply_text(
            "If you're not gonna give me a message to meme, at least give me some catnip..."
        )

    else:
        update.effective_message.reply_to_message.reply_markdown(
            sub(
                r'([aeiouAEIOUａｅｉｏｕＡＥＩＯＵ])',
                (r'\1' * randint(3, 10)),
                update.effective_message.reply_to_message.text_markdown,
            )
        )


@run_async
@bot_action("vapor")
def vapor(update: Update, context: CallbackContext):
    """
    Make a message look more ａｅｓｔｈｅｔｉｃ
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    if not context.args and not (
        update.effective_message.reply_to_message and update.effective_message.reply_to_message.text_markdown
    ):
        update.effective_message.reply_text(
            "If you're not gonna give me something to meme then bring some catnip atleast..."
        )
        return

    # get content to vaporwave
    if context.args:
        text = " ".join(context.args)
    else:
        text = update.effective_message.reply_to_message.text

    aesthetic_text = text.translate(dict((i, i + 0xFEE0) for i in range(0x21, 0x7F)))  # make text more ａｅｓｔｈｅｔｉｃ

    # reply with more ａｅｓｔｈｅｔｉｃｓ
    if context.args:
        update.effective_message.reply_markdown(f"`{aesthetic_text}`")
    else:
        update.effective_message.reply_to_message.reply_markdown(f"`{aesthetic_text}`")


__help__ = """
- /mock `<reply>` : MoCk LikE sPOnGEbob

- /zalgofy `<reply>` : cͩ͠o̴͕r͌̈ȓ͡ṵ̠p̟͜tͯ͞ t̷͂ḣ͞ȩ͗ t̪̉e̢̪x̨͑t̼ͨ

- /owo `<reply>` : translate normie to moe weeb

- /stretch `<reply>` : talk like the sloth from zootopia

- /vapor `[<reply>|<message>]` : ｖａｐｏｒｗａｖｅ ａｅｓｔｈｅｔｉｃｓ
"""

__mod_name__ = "memes"

# create handlers
dispatcher.add_handler(CommandHandler("runs", runs))
dispatcher.add_handler(CommandHandler("mock", mock))
dispatcher.add_handler(CommandHandler("zalgofy", zalgofy))
dispatcher.add_handler(CommandHandler("owo", owo))
dispatcher.add_handler(CommandHandler("stretch", stretch))
dispatcher.add_handler(CommandHandler("vapor", vapor))
