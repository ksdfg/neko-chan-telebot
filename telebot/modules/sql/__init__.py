from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from telebot import config
from .models import Base

engine = create_engine(config.DB_URI)
Session = sessionmaker(engine)
session = Session()

Base.metadata.create_all(engine)
