from re import compile, search
from subprocess import Popen, PIPE, check_output, CalledProcessError, STDOUT

from telegram import MAX_MESSAGE_LENGTH, Update
from telegram.ext import CallbackContext, MessageHandler, Filters

from telebot import dispatcher
from telebot.functions import bot_action


@bot_action("regex")
def regex(update: Update, context: CallbackContext):
    """
    Replace text using sed and regex
    :param update: object representing the incoming update.
    :param context: object containing data about the command call.
    """
    if not update.effective_message.reply_to_message:
        update.effective_message.reply_text("Gimme text to replace stuff in, baka!")
        return

    # make sure `s` command is properly terminated
    command = update.effective_message.text
    delimiter = command[1]
    if command.count(delimiter) == 2:
        command += delimiter
    command = search(f"s{delimiter}.*{delimiter}.*{delimiter}[ig]*", command).group()

    # execute sed in shell to get output
    try:
        text_input = Popen(("echo", update.effective_message.reply_to_message.text), stdout=PIPE, stderr=STDOUT)
        result = check_output(("sed", "-r", command), stdin=text_input.stdout, stderr=STDOUT)
    except CalledProcessError as e:
        update.effective_message.reply_markdown(f"```{e.output.decode()}```")
        return

    # reply with the output text
    if len(result.decode()) > MAX_MESSAGE_LENGTH:
        update.effective_message.reply_text("Resultant message is too big for this pussy to send......")
    else:
        update.effective_message.reply_to_message.reply_text(result.decode())


__mod_name__ = "Regex"

__help__ = f"""
- `s/<text1>/<text2>/[<flags>]` : Reply to a message with this to perform a sed operation on that message, replacing all \
occurrences of 'text1' with 'text2'. Flags are optional, and currently include 'i' for ignore case, 'g' for global, \
or nothing. Delimiters include `/`, `_`, `|`, and `:`. Text grouping is supported. The resulting message cannot be \
larger than {MAX_MESSAGE_LENGTH} characters.

*Reminder:* Sed uses some special characters to make matching easier, such as these: `+*.?\\`
If you want to use these characters, make sure you escape them!
eg: \\?.
"""

# ad handlers
dispatcher.add_handler(MessageHandler(Filters.regex(compile("s([/:|_]).*([/:|_]).*")), regex, run_async=True))
