from sqlalchemy import Column, String, ARRAY, BIGINT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class CommandExceptionGroups(Base):
    __tablename__ = "CommandExceptionGroups"

    command = Column(String, primary_key=True)
    groups = Column(ARRAY(BIGINT))
