from copy import deepcopy

from sqlalchemy import Column, String, cast
from sqlalchemy.dialects.postgresql import ARRAY, BIGINT, array

from telebot.modules.sql import session, Base


# create models for this module
class CommandExceptionGroups(Base):
    __tablename__ = "CommandExceptionGroups"

    command = Column(String, primary_key=True)
    groups = Column(ARRAY(BIGINT))


# create the tables for the models
CommandExceptionGroups.__table__.create(checkfirst=True)


"""
create helper functions to be used to interact with the model
"""


def get_command_exception_groups(command: str) -> list:
    exceptions = session.query(CommandExceptionGroups).filter(CommandExceptionGroups.command == command).first()

    if exceptions:
        return exceptions.groups
    else:
        return []


def add_command_exception_groups(command: str, group: int) -> str:
    exceptions = session.query(CommandExceptionGroups).filter(CommandExceptionGroups.command == command).first()

    if exceptions:
        if group in exceptions.groups:
            return f"Exception for command `{command}` already added!"
        else:
            exceptions.groups = exceptions.groups + [group]
            session.commit()

    else:
        session.add(CommandExceptionGroups(command=command, groups=[group]))
        session.commit()

    return f"Exception for command `{command}` added!"


def del_command_exception_groups(command: str, group: int) -> str:
    exceptions = session.query(CommandExceptionGroups).filter(CommandExceptionGroups.command == command).first()

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
    arr = cast(array(tuple([group])), ARRAY(BIGINT))
    exceptions = session.query(CommandExceptionGroups).filter(CommandExceptionGroups.groups >= arr).all()

    if exceptions:
        return [x.command for x in exceptions]
    else:
        return []
