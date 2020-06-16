from copy import deepcopy

from . import session, models


def get_command_exception_groups(command: str) -> list:
    exceptions = (
        session.query(models.CommandExceptionGroups).filter(models.CommandExceptionGroups.command == command).first()
    )

    if exceptions:
        return exceptions.groups
    else:
        return []


def add_command_exception_groups(command: str, group: int) -> str:
    exceptions = (
        session.query(models.CommandExceptionGroups).filter(models.CommandExceptionGroups.command == command).first()
    )

    if exceptions:
        if group in exceptions.groups:
            return f"Exception for command `{command}` already added!"
        else:
            exceptions.groups = exceptions.groups + [group]
            session.commit()

    else:
        session.add(models.CommandExceptionGroups(command=command, groups=[group]))
        session.commit()

    return f"Exception for command `{command}` added!"


def del_command_exception_groups(command: str, group: int) -> str:
    exceptions = (
        session.query(models.CommandExceptionGroups).filter(models.CommandExceptionGroups.command == command).first()
    )

    if exceptions:
        try:
            groups = deepcopy(exceptions.groups)
            groups.remove(group)
            if groups:
                exceptions.groups = groups
            else:
                session.delete(exceptions)
            session.commit()

            return f"Exception for command `{command}` deleted!"

        except ValueError:
            return f"Exception for command `{command}` not added!"

    else:
        return f"Exception for command `{command}` not added!"


def get_exceptions_for_group(group: int) -> list:
    exceptions = (
        session.query(models.CommandExceptionGroups).filter(models.CommandExceptionGroups.groups >= [group]).all()
    )

    if exceptions:
        return [x.command for x in exceptions]
    else:
        return []
