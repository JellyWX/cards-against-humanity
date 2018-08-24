from flask import redirect, url_for, render_template, request, session, abort, jsonify
from flask_socketio import join_room, leave_room, send, emit, rooms
from app import app, db, socketio
from app.models import BlackCards, WhiteCards, Card, Player, Game
import time
import json
from  sqlalchemy.sql.expression import func
import uuid


@socketio.on('join')
def on_join():
    player = Player.query.get(
        session['player']
    )

    player.sid = request.sid
    uuid = player.uuid
    nickname = player.nickname

    game = player.game.id
    join_room(game)
    emit('player_join', (nickname, uuid), room=game)

    db.session.commit()


@socketio.on('leave')
def on_leave():
    player = Player.query.get(
        session['player']
    )

    uuid = player.uuid
    game = player.game.id
    leave_room(game)
    emit('player_leave', (uuid, ), room=game)


@socketio.on('play')
def play(data):
    player = Player.query.get(
        session['player']
    )

    current = player.hand.filter(Card.playing).first()
    if current is not None:
        current.playing = False

    player.ready = True
    player.hand[data].playing = True

    room = rooms()[0]
    print('{} card has been played by {}'.format(player.hand[data], player.nickname))
    emit('ready', (player.uuid, ), room=room)
    game = Game.query.get(player.game.id)

    if all([player.ready for player in game.players]):
        text = ''
        for p in game.players.order_by(func.random()):
            if not p.czar:
                card_q = p.hand.filter(Card.playing)
                card = card_q.first()

                text += card.card.text + '\t'

                card_q.delete(synchronize_session='fetch')

                c = Card(card=WhiteCards.query.order_by(func.random()).first(), hand=p)
                db.session.add(c)

                hand = ''
                for card in p.hand:
                    hand += card.card.text + '\t'

                emit('new_hand', (hand, ), room=p.sid)

        emit('show_cards', (text, ), room=room)

    db.session.commit()


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':

        password = request.form.get('password')

        if password == '':
            password = None

        g = Game(password=password)

        db.session.add(g)
        db.session.commit()

        return redirect( url_for('new_player', game=g.id) )

    elif request.method == 'GET':

        return render_template('index.html')


@app.route('/game')
def game():

    game = Game.query.get(
        request.args.get('id')
    )

    if game is None:

        return redirect( url_for('index') )

    player = Player.query.get(
        session.get('player')
    )

    if player is None:

        return redirect( url_for('new_player', game=game.id) )


    if request.method == 'GET':

        while player.hand.count() < 8:
            c = Card(card=WhiteCards.query.order_by(func.random()).first(), hand=player)
            db.session.add(c)
            db.session.commit()

        return render_template( 'game.html', player=player, game=game )


@app.route('/new_player', methods=['GET', 'POST'])
def new_player():

    game = Game.query.get(
        request.args.get('game')
    )

    if game is None:

        return redirect( url_for('index') )


    if request.method == 'POST':

        if request.form.get('nickname') == '':

            return render_template('new_player.html', errors=['Please enter a nickname'])


        p = Player(nickname=request.form.get('nickname'), game=game, uuid=uuid.uuid4().hex)

        db.session.add(p)
        db.session.commit()

        session['player'] = p.id

        return redirect( url_for('game', id=game.id) )

    elif request.method == 'GET':

        return render_template('new_player.html', errors=[])
