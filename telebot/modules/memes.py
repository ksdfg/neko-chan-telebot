from os.path import join, dirname
from random import choice, randint
from re import sub

from spongemock.spongemock import mock as mock_text
from telegram import Update
from telegram.error import BadRequest
from telegram.ext import CommandHandler, ContextTypes
from zalgo_text.zalgo import zalgo

from telebot import application
from telebot.modules.db.users import add_user
from telebot.utils import bot_action, CommandDescription, check_command


@bot_action("runs")
@check_command("runs")
async def runs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Insulting reply whenever someone uses /runs
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    await update.effective_message.reply_markdown("I'm a cute kitty, and here we have a fat pussy.")
    await update.effective_chat.send_sticker("CAACAgUAAxkBAAIJK19CjPoyyX9QwwHfNOZMnqww1hxXAALfAAPd6BozJDBFCIENpGkbBA")


@bot_action("mock")
@check_command("mock")
async def mock(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Mock a message like spongebob, and reply
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    if context.args:
        await update.effective_message.reply_text(
            mock_text(update.effective_message.text.replace("/mock ", "").strip())
        )

    elif update.effective_message.reply_to_message and update.effective_message.reply_to_message.text:
        await update.effective_message.reply_to_message.reply_text(
            mock_text(update.effective_message.reply_to_message.text)
        )
        # for future usage
        add_user(
            user_id=update.effective_message.reply_to_message.from_user.id,
            username=update.effective_message.reply_to_message.from_user.username,
        )

    else:
        await update.effective_message.reply_text("I don't see anything to mock here other than your ugly face...")


@bot_action("zalgofy")
@check_command("zalgofy")
async def zalgofy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Corrupt the way the text looks, and reply
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    transform = zalgo().zalgofy

    if context.args:
        await update.effective_message.reply_text(
            transform(update.effective_message.text.replace("/zalgofy ", "").strip())
        )

    elif update.effective_message.reply_to_message and update.effective_message.reply_to_message.text:
        await update.effective_message.reply_to_message.reply_text(
            transform(update.effective_message.reply_to_message.text)
        )
        # for future usage
        add_user(
            user_id=update.effective_message.reply_to_message.from_user.id,
            username=update.effective_message.reply_to_message.from_user.username,
        )

    else:
        await update.effective_message.reply_text("Gimme a message to zalgofy before I claw your tits off...")


@bot_action("owo")
@check_command("owo")
async def owo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
        kaomoji = (
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
        )

        # replace certain characters and add a kaomoji
        reply_text = sub(r"[rl]", "w", text)
        reply_text = sub(r"[ｒｌ]", "ｗ", reply_text)
        reply_text = sub(r"[RL]", "W", reply_text)
        reply_text = sub(r"[ＲＬ]", "Ｗ", reply_text)
        reply_text = sub(r"n([aeiouａｅｉｏｕ])", r"ny\1", reply_text)
        reply_text = sub(r"ｎ([ａｅｉｏｕ])", r"ｎｙ\1", reply_text)
        reply_text = sub(r"N([aeiouAEIOU])", r"Ny\1", reply_text)
        reply_text = sub(r"Ｎ([ａｅｉｏｕＡＥＩＯＵ])", r"Ｎｙ\1", reply_text)
        reply_text = sub(r"!+", " " + choice(kaomoji), reply_text)
        reply_text = sub(r"！+", " " + choice(kaomoji), reply_text)
        reply_text = reply_text.replace("ove", "uv")
        reply_text = reply_text.replace("ｏｖｅ", "ｕｖ")
        reply_text += " " + choice(kaomoji)

        return reply_text

    if context.args:
        try:
            await update.effective_message.reply_markdown_v2(
                transform(update.effective_message.text_markdown_v2.replace("/owo ", "").strip())
            )
        except BadRequest as e:
            print(e)
            # in case we messed up markdown while replacing characters and adding kaomoji
            await update.effective_message.reply_text(
                "Gommenye, I over-owo'd myself.... please try again. "
                "If it still doesn't work, then this must be the language of god's you're trying to translate...."
            )

    elif update.effective_message.reply_to_message and update.effective_message.reply_to_message.text:
        try:
            await update.effective_message.reply_to_message.reply_markdown(
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
            await update.effective_message.reply_text(
                "Gommenye, I over-owo'd myself.... please try again. "
                "If it still doesn't work, then this must be the language of god's you're trying to translate...."
            )

    else:
        await update.effective_message.reply_text(
            "Gommenye, I don't nyaruhodo what normie text you want to henshin into the moe weeb dialect"
        )


@bot_action("stretch")
@check_command("stretch")
async def stretch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Stretch the vowels in a message by a random count
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    if context.args:
        await update.effective_message.reply_markdown(
            sub(
                r"([aeiouAEIOUａｅｉｏｕＡＥＩＯＵ])",
                (r"\1" * randint(3, 10)),
                await update.effective_message.text_markdown.replace("/stretch ", "").strip(),
            )
        )

    elif update.effective_message.reply_to_message and update.effective_message.reply_to_message.text:
        await update.effective_message.reply_to_message.reply_markdown(
            sub(
                r"([aeiouAEIOUａｅｉｏｕＡＥＩＯＵ])",
                (r"\1" * randint(3, 10)),
                update.effective_message.reply_to_message.text_markdown,
            )
        )
        # for future usage
        add_user(
            user_id=update.effective_message.reply_to_message.from_user.id,
            username=update.effective_message.reply_to_message.from_user.username,
        )

    else:
        await update.effective_message.reply_text(
            "If you're not gonna give me something to meme then bring some catnip atleast..."
        )


@bot_action("vapor")
@check_command("vapor")
async def vapor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Make a message look more ａｅｓｔｈｅｔｉｃ
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    if not context.args and not (
        update.effective_message.reply_to_message and update.effective_message.reply_to_message.text
    ):
        await update.effective_message.reply_text(
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
        await update.effective_message.reply_markdown(f"`{aesthetic_text}`")
    else:
        await update.effective_message.reply_to_message.reply_markdown(f"`{aesthetic_text}`")


@bot_action("sadge")
@check_command("sadge")
async def sadge(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Quotes from Bennett Foddy's Getting over it
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    with open(join(dirname(__file__), "assets", "bennett_foddy.txt"), "r") as f:
        bennett_foddy: list[str] = [line.strip() for line in f.read().split("---")]

    # If user replied to an original message, let quote be a reply to that message
    if update.effective_message.reply_to_message:
        await update.effective_message.reply_to_message.reply_markdown(f"```\n{choice(bennett_foddy)}\n```")
    else:
        await update.effective_chat.send_message(f"```\n{choice(bennett_foddy)}\n```", parse_mode="markdown")


__help__ = """
- /mock `<reply|message>` : MoCk LikE sPOnGEbob

- /zalgofy `<reply|message>` : cͩ͠o̴͕r͌̈ȓ͡ṵ̠p̟͜tͯ͞ t̷͂ḣ͞ȩ͗ t̪̉e̢̪x̨͑t̼ͨ

- /owo `<reply|message>` : translate normie to moe weeb

- /stretch `<reply|message>` : talk like the sloth from zootopia

- /vapor `<reply|message>` : ｖａｐｏｒｗａｖｅ ａｅｓｔｈｅｔｉｃｓ
"""

__mod_name__ = "memes"

__commands__ = (
    CommandDescription(command="mock", args="<reply|message>", description="MoCk LikE sPOnGEbob"),
    CommandDescription(
        command="zalgofy", args="<reply|message>", description="ͩ͠o̴͕r͌̈ȓ͡ṵ̠p̟͜tͯ͞ t̷͂ḣ͞ȩ͗ t̪̉e̢̪x̨͑t̼ͨ"
    ),
    CommandDescription(command="owo", args="<reply|message>", description="translate normie to moe weeb"),
    CommandDescription(command="stretch", args="<reply|message>", description="talk like the sloth from zootopia"),
    CommandDescription(command="vapor", args="<reply|message>", description="ｖａｐｏｒｗａｖｅ ａｅｓｔｈｅｔｉｃｓ"),
    CommandDescription(command="sadge", args="<reply>", description="try getting over it"),
)

# create handlers
application.add_handler(CommandHandler("runs", runs, block=False))
application.add_handler(CommandHandler("mock", mock, block=False))
application.add_handler(CommandHandler("zalgofy", zalgofy, block=False))
application.add_handler(CommandHandler("owo", owo, block=False))
application.add_handler(CommandHandler("stretch", stretch, block=False))
application.add_handler(CommandHandler("vapor", vapor, block=False))
application.add_handler(CommandHandler("sadge", sadge, block=False))
