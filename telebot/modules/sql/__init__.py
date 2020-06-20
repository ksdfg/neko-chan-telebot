from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from telebot import config

Base = declarative_base()

engine = create_engine(config.DB_URI, client_encoding="utf8")
Base.metadata.bind = engine
Base.metadata.create_all(engine)

session = scoped_session(sessionmaker(bind=engine, autoflush=False))
