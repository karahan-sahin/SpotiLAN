import os

from flask import Flask, render_template, request, jsonify, current_app
from src.utils.search import Searcher

# from src.utils.audio_player import AudioPlayer

app = Flask(__name__)
client = None
search = Searcher()
player = None

def set_params(c, **kwargs):
    global client
    client = c

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
        player.play()
        pass
    elif action == 'pause':
        player.pause()
        pass
    elif action == 'next':
        player.next()
        pass
    elif action == 'previous':
        player.previous()

    response = {'message': 'Request received'}
    return response, 200


@app.route('/api/song-list', methods=['GET'])
def get_song_list():
    return jsonify({'song_list': ["1", "2", "3"]})


@app.route('/api/host-list', methods=['GET'])
def get_host_list():
    return jsonify({'host_list': ["1", "2", "3"]})


@app.route('/api/search', methods=['POST'])
def search_song():
    data = request.get_json()
    query = data.get('query')
    search_results = search.searchSong(query, topN=5)
    print(search_results)
    return jsonify({'search-results': search_results})


@app.route('/api/download', methods=['POST'])
def download_song():
    data = request.get_json()
    url = data.get('url')
    status = search.downloadSong(url, './musics/')
    response = {'message': status}
    return response, 200
