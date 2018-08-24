import json
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Text
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class BlackCards(Base):
    __tablename__ = 'blackcards'

    id = Column(Integer, primary_key=True, unique=True)
    text = Column(Text)


class WhiteCards(Base):
    __tablename__ = 'whitecards'

    id = Column(Integer, primary_key=True, unique=True)
    text = Column(Text)


engine = create_engine('sqlite:///cards.db')
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()

whites = []
with open('whitecards.json', 'r') as f:
    whites = json.load(f)

blacks = []
with open('blackcards.json', 'r') as f:
    blacks = json.load(f)

for white in whites:
    c = WhiteCards(text=white)

    session.add(c)

for black in blacks:
    c = BlackCards(text=black)

    session.add(c)

session.commit()
