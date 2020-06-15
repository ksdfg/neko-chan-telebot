from . import session, models


def get_command_exception_groups(command: str) -> list:
    exceptions = (
        session.query(models.CommandExceptionGroups).filter(models.CommandExceptionGroups.command == command).first()
    )

    if exceptions:
        return exceptions.groups
    else:
        return []
