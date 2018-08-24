from flask import redirect, url_for, render_template, request, session, abort, jsonify
from flask_socketio import join_room, leave_room, send, emit, rooms
from app import app, db, socketio
from app.models import BlackCards, WhiteCards, Card, Player, Game
import time
import json
from  sqlalchemy.sql.expression import func
import uuid


@socketio.on('join')
def on_join(data):
    player = Player.query.get(
        session['player']
    )

    uuid = player.uuid
    nickname = player.nickname

    game = data['game']
    join_room(game)
    emit('player_join', (nickname, uuid), room=game)


@socketio.on('leave')
def on_leave(data):
    player = Player.query.get(
        session['player']
    )

    uuid = player.uuid
    game = data['game']
    leave_room(game)
    emit('player_leave', (uuid, ), room=game)


@socketio.on('play')
def play(data):
    player = Player.query.get(
        session['player']
    )
    player.played = True
    player.hand[data].playing = True

    room = rooms()[0]
    emit('ready', (player.uuid, ), room=room)


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
