import logging

from flask import Flask, jsonify, request, send_from_directory
from flask import Response
from flask_cors import CORS, cross_origin

#from flask import Flask
app = Flask(__name__, static_url_path='')

cors = CORS(app)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/html/<path:path>")
def send_html(path):
    return send_from_directory('html', path)

@app.route("/start")
def start_game():
    return "Start Game!"

@app.route("/stop")
def stop_game():
    return "Stop Game!"

@app.route("/play")
def play_game():
    return "Play Game!"

if __name__ == '__main__':
    #init_log()
    logging.info("server starting...")
    app.run(debug=True)