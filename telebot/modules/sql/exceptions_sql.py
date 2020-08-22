from copy import deepcopy

from mongoengine import Document, StringField, ListField, IntField


# create models for this module
class CommandExceptionGroups(Document):
    command = StringField(required=True)
    groups = ListField(IntField())


"""
create helper functions to be used to interact with the model
"""


def get_command_exception_groups(command: str) -> list:
    exceptions = CommandExceptionGroups.objects(command=command)

    if exceptions:
        return exceptions[0].groups
    else:
        return []


def add_command_exception_groups(command: str, group: int) -> str:
    exceptions_list = CommandExceptionGroups.objects(command=command)

    if exceptions_list:
        exceptions = exceptions_list[0]
        if group in exceptions.groups:
            return f"Exception for command `{command}` already added!"
        else:
            exceptions.groups = exceptions.groups + [group]
            exceptions.save()

    else:
        CommandExceptionGroups(command=command, groups=[group]).save()

    return f"Exception for command `{command}` added!"


def del_command_exception_groups(command: str, group: int) -> str:
    exceptions_list = CommandExceptionGroups.objects(command=command)

    if exceptions_list:
        exceptions = exceptions_list[0]
        try:
            groups = deepcopy(exceptions.groups)
            groups.remove(group)
            if groups:
                exceptions.groups = groups
                exceptions.save()
            else:
                exceptions.delete()

            return f"Exception for command `{command}` deleted!"

        except ValueError:
            return f"Exception for command `{command}` not added!"

    else:
        return f"Exception for command `{command}` not added!"


def get_exceptions_for_group(group: int) -> list:
    exceptions = CommandExceptionGroups.objects(groups=group)

    if exceptions:
        return [x.command for x in exceptions]
    else:
        return []
