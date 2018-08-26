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

    is_czar = False

    for p in player.game.players:
        if p.czar:
            is_czar = True

        if p.uuid != player.uuid:
            emit('player_join', (p.nickname, p.uuid, p.czar, p.points), room=player.sid)

    if not is_czar:
        player.czar = True

    emit('player_join', (nickname, uuid, player.czar, player.points), room=game)

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
    game = Game.query.get(player.game.id)

    if game.stage == 'czar':
        print('attempt to play during czar stage')
        return

    current = player.hand.filter(Card.playing)
    while current.count() > game.card.spaces:
        current.first().playing = False

    player.hand[data].playing = True

    if current.count() == game.card.spaces:
        player.ready = True
    else:
        player.ready = False

    db.session.commit()

    print('{} card has been played by {}'.format(player.hand[data], player.nickname))

    emit('ready', (player.uuid, ), room=game.id)

    if all([player.ready for player in game.players if not player.czar]):
        game.stage = 'czar'

        text = ''
        for p in game.players.order_by(func.random()):
            if not p.czar:
                card_q = p.hand.filter(Card.playing)

                new = '\\'.join([c.card.text for c in card_q])

                text += new + '\t'

        print(text)

        emit('show_cards', (text, ), room=game.id)

    db.session.commit()


@socketio.on('czar_select')
def czar_select(text):
    player = Player.query.get(
        session['player']
    )

    if player.czar:
        old_czar = player.id

        player.game.stage = 'selecting'

        for p in player.game.players.order_by(func.random()):
            if not p.uuid == player.uuid:
                card_text = p.hand.filter(Card.playing).first().card.text

                if card_text == text:
                    p.points += 1
                    emit('round_win', (p.uuid, ), room=player.game.id)

                    break

        else:
            return

        point_board = {}

        for p in player.game.players.order_by(Player.id):
            p.hand.filter(Card.playing).delete(synchronize_session='fetch')
            p.czar = False

            point_board[p.uuid] = p.points

            while p.hand.count() < 8:
                c = Card(card=WhiteCards.query.order_by(func.random()).first(), hand=p)
                db.session.add(c)

        player.game.card = BlackCards.query.order_by(func.random()).first()

        new_czar = player.game.players.order_by(func.random()).first()

        while new_czar.id == old_czar:
            new_czar = player.game.players.order_by(func.random()).first()

        new_czar.czar = True

        db.session.commit()

        for p in player.game.players:
            p.ready = False
            print(p.nickname)
            cards = '\t'.join([x.card.text for x in p.hand.order_by(Card.id)])

            emit('refresh', (cards, new_czar.uuid, player.game.card.text, point_board, ), room=p.sid)

        db.session.commit()


@socketio.on('send_message')
def send_message(text):
    player = Player.query.get(
        session['player']
    )

    emit('message', (player.uuid, text), room=player.game.id)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':

        password = request.form.get('password')

        if password == '':
            password = None

        g = Game(password=password, card=BlackCards.query.order_by(func.random()).first())

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


    if 'player' not in session:
        return redirect( url_for('new_player', game=game.id) )


    player = Player.query.get(
        session.get('player')
    )

    if player is None or player.game.id != game.id:

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

            return render_template('new_player.html', errors=['You must enter a nickname'], password=game.password is not None)

        if game.password is not None:
            if request.form.get('password') != game.password:

                return render_template('new_player.html', errors=['Password is incorrect'], password=True)

        p = Player(nickname=request.form.get('nickname'), game=game, uuid=uuid.uuid4().hex)

        db.session.add(p)
        db.session.commit()

        session['player'] = p.id

        return redirect( url_for('game', id=game.id) )

    elif request.method == 'GET':

        return render_template('new_player.html', errors=[], password=game.password is not None)
