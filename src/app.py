from flask import Flask, render_template, request, jsonify, current_app

app = Flask(__name__)
client = None


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
        print("play")
        pass
    elif action == 'pause':
        print("pause")
        pass
    elif action == 'next':
        print("next")
        pass
    elif action == 'previous':
        print('previous')

    response = {'message': 'Request received'}
    return response, 200


@app.route('/api/song-list', methods=['GET'])
def get_song_list():
    return jsonify({'song_list': ["1", "4", "3", "2", "4", "5"]})


@app.route('/api/host-list', methods=['GET'])
def get_host_list():
    return jsonify({'host_list': ["1", "2", "3"]})
