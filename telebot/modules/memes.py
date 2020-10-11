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
from telebot.modules.db.users import add_user


@bot_action("runs")
def runs(update: Update, context: CallbackContext) -> None:
    """
    Insulting reply whenever someone uses /runs
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    update.effective_message.reply_markdown("I'm a cute kitty, and here we have a fat pussy.")
    update.effective_chat.send_sticker("CAACAgUAAxkBAAIJK19CjPoyyX9QwwHfNOZMnqww1hxXAALfAAPd6BozJDBFCIENpGkbBA")


@bot_action("mock")
def mock(update: Update, context: CallbackContext) -> None:
    """
    Mock a message like spongebob, and reply
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    if update.effective_message.reply_to_message:
        # for future usage
        add_user(
            user_id=update.effective_message.reply_to_message.from_user.id,
            username=update.effective_message.reply_to_message.from_user.username,
        )

        update.effective_message.reply_to_message.reply_text(mock_text(update.effective_message.reply_to_message.text))

    else:
        update.effective_message.reply_text("I don't see anything to mock here other than your ugly face...")


@bot_action("zalgofy")
def zalgofy(update: Update, context: CallbackContext) -> None:
    """
    Corrupt the way the text looks, and reply
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    transform = zalgo().zalgofy

    if context.args:
        update.effective_message.reply_text(transform(update.effective_message.text.replace("/zalgofy ", "").strip()))

    elif update.effective_message.reply_to_message:
        # for future usage
        add_user(
            user_id=update.effective_message.reply_to_message.from_user.id,
            username=update.effective_message.reply_to_message.from_user.username,
        )
        update.effective_message.reply_to_message.reply_text(transform(update.effective_message.reply_to_message.text))

    else:
        update.effective_message.reply_text("Gimme a message to zalgofy before I claw your tits off...")


@bot_action("owo")
def owo(update: Update, context: CallbackContext) -> None:
    """
    Change a message to look like it was said by a moe weeb
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """

    def transform(text: str):
        """
        Transform message text
        :param text: The text in the message
        :return: owo-fied text
        """
        # list of all kaomojis to use in owo
        kaomoji = [
            r"`(・\`ω´・)`",
            "`;;w;;`",
            "`owo`",
            "`UwU`",
            "`>w<`",
            "`^w^`",
            "`( ^ _ ^)∠☆`",
            "`(ô_ô)`",
            "`~:o`",
            "`;____;`",
            "`(*^*)`",
            "`(>_`",
            "`(♥_♥)`",
            "`*(^O^)*`",
            "`((+_+))`",
        ]

        # replace certain characters and add a kaomoji
        reply_text = sub(r'[rl]', "w", text)
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
        reply_text += " " + choice(kaomoji)

        return reply_text

    if context.args:
        try:
            update.effective_message.reply_markdown_v2(
                transform(update.effective_message.text_markdown_v2.replace("/owo ", "").strip())
            )
        except BadRequest as e:
            print(e)
            # in case we messed up markdown while replacing characters and adding kaomoji
            update.effective_message.reply_text(
                "Gommenye, I over-owo'd myself.... please try again. "
                "If it still doesn't work, then this must be the language of god's you're trying to translate...."
            )

    elif update.effective_message.reply_to_message:
        try:
            print(transform(update.effective_message.reply_to_message.text_markdown))
            update.effective_message.reply_to_message.reply_markdown(
                transform(update.effective_message.reply_to_message.text_markdown)
            )
            # for future usage
            add_user(
                user_id=update.effective_message.reply_to_message.from_user.id,
                username=update.effective_message.reply_to_message.from_user.username,
            )
        except BadRequest as e:
            print(e)
            # in case we messed up markdown while replacing characters and adding kaomoji
            update.effective_message.reply_text(
                "Gommenye, I over-owo'd myself.... please try again. "
                "If it still doesn't work, then this must be the language of god's you're trying to translate...."
            )

    else:
        update.effective_message.reply_text(
            "Gommenye, I don't nyaruhodo what normie text you want to henshin into the moe weeb dialect"
        )


@bot_action("stretch")
def stretch(update: Update, context: CallbackContext):
    """
    Stretch the vowels in a message by a random count
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    if context.args:
        update.effective_message.reply_markdown(
            sub(
                r'([aeiouAEIOUａｅｉｏｕＡＥＩＯＵ])',
                (r'\1' * randint(3, 10)),
                update.effective_message.text_markdown.replace("/stretch ", "").strip(),
            )
        )

    elif update.effective_message.reply_to_message:
        update.effective_message.reply_to_message.reply_markdown(
            sub(
                r'([aeiouAEIOUａｅｉｏｕＡＥＩＯＵ])',
                (r'\1' * randint(3, 10)),
                update.effective_message.reply_to_message.text_markdown,
            )
        )
        # for future usage
        add_user(
            user_id=update.effective_message.reply_to_message.from_user.id,
            username=update.effective_message.reply_to_message.from_user.username,
        )

    else:
        update.effective_message.reply_text(
            "If you're not gonna give me something to meme then bring some catnip atleast..."
        )


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
        # for future usage
        add_user(
            user_id=update.effective_message.reply_to_message.from_user.id,
            username=update.effective_message.reply_to_message.from_user.username,
        )

    aesthetic_text = text.translate(dict((i, i + 0xFEE0) for i in range(0x21, 0x7F)))  # make text more ａｅｓｔｈｅｔｉｃ

    # reply with more ａｅｓｔｈｅｔｉｃｓ
    if context.args:
        update.effective_message.reply_markdown(f"`{aesthetic_text}`")
    else:
        update.effective_message.reply_to_message.reply_markdown(f"`{aesthetic_text}`")


__help__ = """
- /mock `<reply>` : MoCk LikE sPOnGEbob

- /zalgofy `<reply|message>` : cͩ͠o̴͕r͌̈ȓ͡ṵ̠p̟͜tͯ͞ t̷͂ḣ͞ȩ͗ t̪̉e̢̪x̨͑t̼ͨ

- /owo `<reply|message>` : translate normie to moe weeb

- /stretch `<reply|message>` : talk like the sloth from zootopia

- /vapor `<reply|message>` : ｖａｐｏｒｗａｖｅ ａｅｓｔｈｅｔｉｃｓ
"""

__mod_name__ = "memes"

# create handlers
dispatcher.add_handler(CommandHandler("runs", runs, run_async=True))
dispatcher.add_handler(CommandHandler("mock", mock, run_async=True))
dispatcher.add_handler(CommandHandler("zalgofy", zalgofy, run_async=True))
dispatcher.add_handler(CommandHandler("owo", owo, run_async=True))
dispatcher.add_handler(CommandHandler("stretch", stretch, run_async=True))
dispatcher.add_handler(CommandHandler("vapor", vapor, run_async=True))
