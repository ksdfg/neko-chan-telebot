from re import compile, search
from subprocess import Popen, PIPE, check_output, CalledProcessError, STDOUT

from telegram import MAX_MESSAGE_LENGTH, Update
from telegram.ext import CallbackContext, MessageHandler, Filters

from telebot import dispatcher
from telebot.functions import bot_action
from telebot.modules.db.exceptions import get_exceptions_for_chat


@bot_action("regex")
def regex(update: Update, context: CallbackContext):
    """
    Replace text using sed and regex
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    if "regex" in get_exceptions_for_chat(update.effective_chat.id):
        return

    # check if there is a quoted message
    if not (
        update.effective_message.reply_to_message
        and (update.effective_message.reply_to_message.text or update.effective_message.reply_to_message.caption)
    ):
        update.effective_message.reply_text("Gimme text to replace stuff in, baka!")
        return

    # make sure `s` command is properly terminated
    command = update.effective_message.text
    delimiter = command[1]
    if command.replace(f'\\{delimiter}', '').count(delimiter) == 2:
        command += delimiter
    delimiter_regex_safe = delimiter.replace('|', r'\|')  # because | is regex OR
    command = search(f"s{delimiter_regex_safe}.*{delimiter_regex_safe}.*{delimiter_regex_safe}[ig]*", command).group()

    # execute sed in shell to get output
    content = (
        update.effective_message.reply_to_message.text
        if update.effective_message.reply_to_message.text
        else update.effective_message.reply_to_message.caption
    )
    try:
        text_input = Popen(("echo", content), stdout=PIPE, stderr=STDOUT)
        result = check_output(("sed", "-r", command), stdin=text_input.stdout, stderr=STDOUT)
    except CalledProcessError as e:
        update.effective_message.reply_markdown(f"```{e.output.decode()}```")
        return

    # reply with the output text
    if update.effective_message.reply_to_message.document:
        update.effective_message.reply_to_message.reply_document(
            document=update.effective_message.reply_to_message.document,
            filename=update.effective_message.reply_to_message.document.file_name,
            caption=result.decode('utf-8'),
            reply_markup=update.effective_message.reply_to_message.reply_markup,
        )
    elif update.effective_message.reply_to_message.photo:
        update.effective_message.reply_to_message.reply_photo(
            photo=update.effective_message.reply_to_message.photo[-1].file_id,
            caption=result.decode('utf-8'),
            reply_markup=update.effective_message.reply_to_message.reply_markup,
        )
    elif update.effective_message.reply_to_message.audio:
        update.effective_message.reply_to_message.reply_audio(
            photo=update.effective_message.reply_to_message.audio,
            caption=result.decode('utf-8'),
            reply_markup=update.effective_message.reply_to_message.reply_markup,
        )
    elif update.effective_message.reply_to_message.voice:
        update.effective_message.reply_to_message.reply_voice(
            photo=update.effective_message.reply_to_message.voice,
            caption=result.decode('utf-8'),
            reply_markup=update.effective_message.reply_to_message.reply_markup,
        )
    elif update.effective_message.reply_to_message.video:
        update.effective_message.reply_to_message.reply_video(
            photo=update.effective_message.reply_to_message.video,
            caption=result.decode('utf-8'),
            reply_markup=update.effective_message.reply_to_message.reply_markup,
        )
    else:
        update.effective_message.reply_to_message.reply_text(result.decode('utf-8'))


__mod_name__ = "Regex"

__help__ = f"""
- `s/<text1>/<text2>/[<flags>]` : Reply to a message with this to perform a sed operation on that message, replacing all \
occurrences of 'text1' with 'text2'. Flags are optional, and currently include 'i' for ignore case, 'g' for global, \
or nothing. Delimiters include `/`, `_`, `|`, and `:`. Text grouping is supported. The resulting message cannot be \
larger than {MAX_MESSAGE_LENGTH} characters.

*Reminder:* Sed uses some special characters to make matching easier, such as these: `+*.?\\`
If you want to use these characters, make sure you escape them!
eg: \\?.

Add an exception to `regex` to disable this module.
"""

# ad handlers
dispatcher.add_handler(MessageHandler(Filters.regex(compile("^s([/:|_]).*([/:|_]).*")), regex, run_async=True))
