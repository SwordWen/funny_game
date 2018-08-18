import logging

import json
import uuid

from flask import Flask, jsonify, request, send_from_directory
from flask import Response
from flask_cors import CORS, cross_origin

from uct import Game
from function import init_log

#from flask import Flask
app = Flask(__name__, static_url_path='')

cors = CORS(app)

game_map = {}

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/html/<path:path>")
def send_html(path):
    return send_from_directory('html', path)


"""
{id:'game id'}
"""
@app.route("/start", methods=['POST'])
def start_game():
    logging.debug("start request: " + str(request.json))
    if len(game_map) >= 10:
        logging.debug("can't start game: " + str(request.json))
        return "Can not create game anymore.", 200
    game_id = str(uuid.uuid1())
    game = Game()
    board_size = int(request.json["board_size"])
    win_length = int(request.json["win_length"])
    human_player = int(request.json["human_player"])

    game.start(board_size, win_length, human_player, game_id)
    game_map[game_id] = game
    logging.info("start game:" + game_id)
    logging.debug("total games: " + str(len(game_map)))
    return jsonify({'game_id': game_id}), 200

@app.route("/stop", methods=['POST'])
def stop_game():
    logging.debug("stop request: " + str(request.json))
    game_id = request.json["game_id"]
    if game_id in game_map:
        game_map[game_id].stop()
        del game_map[game_id]
    logging.debug("total games: " + str(len(game_map)))
    return "Stop Game!", 200

@app.route("/play", methods=['POST'])
def play_game():
    logging.debug("play request: " + str(request.json))
    game_id = request.json["game_id"]
    move = int(request.json["move"])
    if game_id in game_map:
        game_map[game_id].play(move)
    else:
        return "can't find game" + str(game_id), 404
    return "play with move" + str(move), 200
    #return "Play Game!" + str(count)

@app.route("/nextstep", methods=['POST'])
def next_step():
    logging.debug("nextstep request: " + str(request.json))
    game_id = request.json["game_id"]
    move = -1
    if game_id in game_map:
        move, winner = game_map[game_id].try_to_get_next_step()
        return  jsonify({'game_id': game_id, 'move': move, 'winner': winner}), 200
    else:
        return "can't find game" + str(game_id), 404
    



#FLASK_APP=server.py flask run
#FLASK_APP=server.py flask run --host=0.0.0.0 --port=8080
if __name__ == '__main__':
    init_log()
    logging.info("server starting...")
    app.run(debug=True)