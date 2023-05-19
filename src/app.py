import flask
from flask import render_template, request, jsonify
from src.utils.search import Searcher
from src.utils.messages import send_message_tcp
from src.configs import config
from src.main import app
import time

search = Searcher()

def action(action_type):
    # calculate delay time + send package
    # send_message_tcp
    agreed_time = time.perf_counter_ns() + config.DELAY
    send_message_tcp(to=flask.g.client.peer.get("ip"), msg={"type": action_type,
                                                            "song": flask.g.player.current_song,
                                                            "timestamp": agreed_time}, port=config.PORT)
    
    player_action = flask.g.player.start if action_type == "start" else flask.g.player.stop
    while True:
        if time.perf_counter_ns() >= agreed_time:
            player_action()

@app.route('/', methods=['GET'])
def home():
    # if client.name:
    return render_template('index.html', song_list=["1", "2", "3", "4"])

@app.route('/api/audio', methods=['POST'])
def handle_request():
    data = request.get_json()
    action = data.get('action')
    
    # Perform actions based on the received action
    if action == 'play':
        action("start")
    elif action == 'pause':
        action("stop")      
    elif action == 'next':
        action("stop")
        flask.g.player.next()
        action("start")
    elif action == 'previous':
        action("stop")
        flask.g.player.prev()
        action("start")

    response = {'message': 'Request received'}
    return response, 200


@app.route('/api/song-list', methods=['GET'])
def get_song_list():
    return jsonify({'song_list': ["1", "2", "3"]})


@app.route('/api/host-list', methods=['GET'])
def get_host_list():
    return jsonify({'host_list': ["1", "2", "3"]})


@app.route('/api/add-song', methods=['POST'])
def search_song():
    data = request.get_json()
    song = data.get('song')
    msg = {
        "type": "add", 
        "id": song.get("id"), 
        "link": song.get("url"), 
        "title": song.get("title")
    }
    send_message_tcp(to=flask.g.client.peer.get("ip"),
                     msg=msg,
                     port=config.PORT)

    response = {'message': 'Request received'}
    return response, 200

@app.route('/api/search', methods=['POST'])
def search_song():
    data = request.get_json()
    query = data.get('query')
    search_results = search.searchSong(query, topN=5)
    response = {'search_results': search_results}
    return response, 200

@app.route('/api/download', methods=['POST'])
def download_song():
    data = request.get_json()
    url = data.get('url')
    status = search.downloadSong(url)   
    response = {'message': status}
    return response, 200