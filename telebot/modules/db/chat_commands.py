from mongoengine import Document, IntField, StringField, ListField
from telegram.utils.helpers import escape_markdown


class ChatCommand(Document):
    chat = IntField(required=True)  # chat ID for which we are storing enabled commands
    enabled_commands = ListField(StringField())  # list of enabled commands for given chat
    disabled_commands = ListField(StringField())  # list of disabled commands for given chat


# create helper functions to be used to interact with the model


def enable_commands_for_chat(chat: int, commands: list[str]) -> list[str]:
    """
    Enable a command for a given chat ID
    :param chat: chat ID to enable commands for
    :param commands: commands to enable for chat
    :return: message to be replied to the user in telegram
    """
    # fetch or initialize chat command for given chat
    if chat_commands := ChatCommand.objects(chat=chat):
        chat_command = chat_commands[0]
    else:
        chat_command = ChatCommand(chat=chat)

    responses: list[str] = []

    # check if command is already enabled
    # if not, append command to the object's enabled commands list, and remove it from the disabled list
    for command in commands:
        if command in chat_command.enabled_commands:
            responses.append(f"Command `{escape_markdown(command)}` is already enabled for given chat")
        else:
            chat_command.enabled_commands.append(command)

            try:
                chat_command.disabled_commands.remove(command)
            except ValueError:
                # doesn't matter if the command was not in the list
                pass

            responses.append(f"Enabled command `{escape_markdown(command)}` for current chat!")

    # update mongo doc
    chat_command.save()
    return responses


def disable_commands_for_chat(chat: int, commands: list[str]) -> list[str]:
    """
    Disable a command for a given chat ID
    :param chat: chat ID to disable command for
    :param commands: command to disable for chat
    :return: message to be replied to the user in telegram
    """
    # fetch or initialize chat command for given chat
    if chat_commands := ChatCommand.objects(chat=chat):
        chat_command = chat_commands[0]
    else:
        chat_command = ChatCommand(chat=chat)

    responses: list[str] = []

    # check if command is already disabled
    # if not, append command to the object's enabled commands list, and remove it from the disabled list
    for command in commands:
        if command in chat_command.disabled_commands:
            responses.append(f"Command `{escape_markdown(command)}` is already disabled for given chat")
        else:
            chat_command.disabled_commands.append(command)

            try:
                chat_command.enabled_commands.remove(command)
            except ValueError:
                # doesn't matter if the command was not in the list
                pass

            responses.append(f"Disabled command `{escape_markdown(command)}` for current chat!")

    # update mongo doc
    chat_command.save()
    return responses


def check_command_for_chat(chat: int, command: str) -> bool:
    """
    Check if a command is in a populated enabled or disabled list
    :param chat: chat ID for which we're checking if the command is enabled
    :param command: command to check
    :return: True if command is enabled, else False
    """
    # if no chat command document exists, then all commands are enabled
    if not (chat_commands := ChatCommand.objects(chat=chat)):
        return True
    chat_command = chat_commands[0]

    # if enabled commands list is populated, then command should be in it for it to be enabled
    if chat_command.enabled_commands and command not in chat_command.enabled_commands:
        return False

    # if command exists in disabled list, then it's disabled.
    if command in chat_command.disabled_commands:
        return False

    return True
