from sqlalchemy import Column, String, ARRAY, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class CommandExceptionGroups(Base):
    __tablename__ = "CommandExceptionGroups"

    command = Column(String, primary_key=True)
    groups = Column(ARRAY(Integer))
