from app import db

class BlackCards(db.Model):
    __tablename__ = 'blackcards'
    __bind_key__ = None

    id = db.Column(db.Integer, primary_key=True, unique=True)
    text = db.Column(db.Text)

    spaces = db.Column(db.Integer, nullable=False, default=1)

    games = db.relationship('Game', backref='card', lazy='dynamic')


class WhiteCards(db.Model):
    __bind_key__ = None
    __tablename__ = 'whitecards'

    id = db.Column(db.Integer, primary_key=True, unique=True)
    text = db.Column(db.Text)

    instances = db.relationship('Card', backref='card', lazy='dynamic')


class Card(db.Model):
    __bind_key__ = 'game'
    __tablename__ = 'cards'

    id = db.Column(db.Integer, primary_key=True, unique=True)
    card_id = db.Column(db.Integer, db.ForeignKey('whitecards.id'))
    hand_id = db.Column(db.Integer, db.ForeignKey('players.id'))

    playing = db.Column(db.Boolean, nullable=False, default=False)

    custom = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return '<WhiteCard instance "{}">'.format(self.card.text)


class Player(db.Model):
    __bind_key__ = 'game'
    __tablename__ = 'players'

    id = db.Column(db.Integer, primary_key=True, unique=True)
    uuid = db.Column(db.Text, unique=True)
    sid = db.Column(db.Text, unique=True)

    nickname = db.Column(db.Text, nullable=False)
    points = db.Column(db.Integer, nullable=False, default=0)
    hand = db.relationship('Card', backref='hand', lazy='dynamic')

    game_id = db.Column(db.Integer, db.ForeignKey('games.id'))

    ready = db.Column(db.Boolean, nullable=False, default=False)
    czar = db.Column(db.Boolean, nullable=False, default=False)


class Game(db.Model):
    __bind_key__ = 'game'
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True, unique=True)

    players = db.relationship('Player', backref='game', lazy='dynamic')
    password = db.Column(db.Text, nullable=True)

    stage = db.Column(db.Text, nullable=False, default='waiting')
    card_id = db.Column(db.Integer, db.ForeignKey('blackcards.id'))

    custom_chance = db.Column(db.Float)
