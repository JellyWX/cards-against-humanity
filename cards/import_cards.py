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

    spaces = Column(Integer, nullable=False, default=1)


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
    spaces = 1
    if black.count('_') < spaces:
        spaces = 1
    else:
        spaces = black.count('_')

    c = BlackCards(text=black, spaces=spaces)

    session.add(c)

session.commit()

# longest card: The collective wail of every Magic player suddenly realizing that they've spent hundreds of dollars on pieces of cardboard.
# longest card: Who blasphemes and bubbles at the center of all infinity, whose name no lips dare speak aloud, and who gnaws hungrily in inconceivable, unlighted chambers beyond time?
