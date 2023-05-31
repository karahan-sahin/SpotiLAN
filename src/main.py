import base64
import json
import argparse
import socket
import time
import random
import flask
import select
import threading
import numpy as np
import concurrent.futures
from flask import render_template, request, jsonify
from src.configs import config
from src.utils.client import Client
from src.utils.search import Searcher
from pydub import AudioSegment, playback
from src.utils.messages import send_message_tcp, send_message_udp, process_tcp_msg, process_udp_msg

# Initialize global variables
client: Client
search: Searcher
app = flask.Flask(__name__)

global ff, queue, curr, playlist

# Create a thread pool with a maximum of 10 threads
executor = concurrent.futures.ThreadPoolExecutor(
    max_workers=config.THREAD_POOL_SIZE)


def tcp_listener(
        port: int = config.MSG_PORT,
        buffer_size: int = config.BUFFER_SIZE,
):
    """
    Listens to the specified host:port socket for TCP messages and sends an answer if the message is valid.
    :param port: Port number to be listened
    :param buffer_size: size of the payload in package
    """
    global client, search, playlist, queue, curr
    print(f"Listening From {port=}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((client.myip, port))
        while True:
            # Listen the socket
            s.listen()
            conn, addr = s.accept()
            with conn:
                msg = ""
                while True:
                    data = conn.recv(buffer_size)
                    if not data:
                        break
                    try:
                        data = base64.b64decode(data)
                        msg += data.decode('utf-8')
                    except Exception as e:
                        raise e
                msg = json.loads(msg)
                executor.submit(process_tcp_msg, msg,
                                addr[0], client, search, queue, playlist, curr)


def udp_listener(
        port: int = config.MSG_PORT,
        buffer_size: int = config.BUFFER_SIZE,
) -> None:
    """
    Listens to the specified port for UDP messages and sends an answer if the message is valid
    :param int port: Port number to broadcast
    :param int buffer_size: Size of message buffer in bytes
    """
    global client
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', port))
        s.setblocking(False)
        while True:
            result = select.select([s], [], [])
            msg, sender = result[0][0].recvfrom(buffer_size)
            if sender[0] != client.myip:
                # submit the package for processing to the thread pool
                executor.submit(process_udp_msg, client, msg,
                                sender[0], config.MSG_PORT)


def udp_broadcaster(
        port: int = config.MSG_PORT,
        period: int = config.BROADCAST_PERIOD,
) -> None:
    """
    Broadcasts the hello message periodically
    :param port: Port number to broadcast
    :param period: period of broadcast
    """
    global client
    while True:
        try:
            msg = client.me
            send_message_udp(msg=msg, port=port)
        except Exception as e:
            raise e
        time.sleep(period)


def clear_cache(
        period: int = config.CACHE_PERIOD
) -> None:
    """
    Clears the known host list periodically
    :param period: period of operation
    """
    global client
    while True:
        time.sleep(period)
        with client.lock:
            client.clear_known_hosts()


def sync(port: int = config.SYNC_PORT) -> None:
    """
    Constantly sending <SYNC> object
    TODO: Add turn flag

    Current Time 1685461528320175000
    Agreed Time  1685461528477618e+18   

    """
    global client
    while True:
        if client.known_hosts:
            name = list(client.known_hosts.keys())[0]
            target_ip = client.known_hosts[name]
            message = {
                "type": "sync",
                "timestamp": time.time_ns(),
            }
            send_message_tcp(to=target_ip, msg=message, port=port)
            time.sleep(0.5)


def actionHandle(action_type, client):
    global ff, queue, curr

    # calculate delay time + send package
    # send_message_tcp
    agreed_time = time.time_ns() + config.DELAY
    agreed_time = int(agreed_time)
    print(time.time_ns())
    print(f"{agreed_time}")

    if action_type == "start":
        with client.lock:
            if client.known_hosts:
                name = list(client.known_hosts.keys())[0]
                target_ip = client.known_hosts[name]
                message = {"type": action_type,
                        "timestamp": agreed_time, 
                        "title": queue[curr]}

                send_message_tcp(to=target_ip,
                                msg=message,
                                port=config.MUSIC_PORT)

            peer_delay = np.mean(client.peer_delay, dtype=int)    
            while True:
                if time.time_ns() - peer_delay >= agreed_time:
                    print("Starting...", )
                    seg = AudioSegment.from_file(
                        "musics/down_from_the_sky.mp3")
                    ff = playback._play_with_simpleaudio(seg)
                    print("Started song")
                    break

    elif action_type == "stop":
        with client.lock:
            if client.known_hosts:
                name = list(client.known_hosts.keys())[0]
                target_ip = client.known_hosts[name]
                message = {"type": action_type,
                        "timestamp": agreed_time, "title": queue[curr]}

                send_message_tcp(to=target_ip,
                                msg=message,
                                port=config.MUSIC_PORT)

            peer_delay = np.mean(client.peer_delay, dtype=int)
            while True:
                if time.time_ns() - peer_delay >= agreed_time:
                    print("Stopping song...")
                    ff.stop()
                    break

    elif action_type == "next":
        with client.lock:
            if client.known_hosts:
                name = list(client.known_hosts.keys())[0]
                target_ip = client.known_hosts[name]
                curr += 1
                message = {"type": action_type,
                        "timestamp": agreed_time, "title": queue[curr]}

                send_message_tcp(to=target_ip,
                                msg=message,
                                port=config.MUSIC_PORT)

            peer_delay = np.mean(client.peer_delay, dtype=int)
            while True:
                if time.time_ns() - peer_delay >= agreed_time:
                    print("Stopping song...")
                    ff.stop()
                    seg = AudioSegment.from_file(queue[curr])
                    ff = playback._play_with_simpleaudio(seg)
                    break

    elif action_type == "previous":
        with client.lock:
            if client.known_hosts:
        
                name = list(client.known_hosts.keys())[0]
                target_ip = client.known_hosts[name]
                curr -= 1
                message = {"type": action_type,
                        "timestamp": agreed_time, "title": queue[curr]}

                send_message_tcp(to=target_ip,
                                msg=message,
                                port=config.MUSIC_PORT)

            peer_delay = np.mean(client.peer_delay, dtype=int)
            while True:
                if time.time_ns() - peer_delay >= agreed_time:
                    print("Stopping song...")
                    ff.stop()
                    seg = AudioSegment.from_file(queue[curr])
                    ff = playback._play_with_simpleaudio(seg)
                    break


@app.route('/', methods=['GET'])
def home():
    global queue, playlist
    # if client.name:
    return render_template('index.html', song_list=playlist, queue_list=queue)


@app.route('/api/audio', methods=['POST'])
def handle_request():

    global client, search
    global queue, playlist
    

    data = request.get_json()
    action = data.get('action')

    # Perform actions based on the received action
    if action == 'play':
        executor.submit(actionHandle, "start", client)
    elif action == 'pause':
        executor.submit(actionHandle, "stop", client)
    elif action == 'next':
        executor.submit(actionHandle, "next", client)
    elif action == 'previous':
        executor.submit(actionHandle, "previous", client)

    response = {'message': 'Request received'}
    return response, 200


@app.route('/api/song-list', methods=['GET'])
def get_play_list():
    global queue, playlist
    return jsonify({'song_list': playlist})


@app.route('/api/queue-list', methods=['GET'])
def get_queue_list():
    global queue, playlist
    print(f"Current queue: {queue=}")
    return jsonify({'queue_list': queue, 'curr': curr})


@app.route('/api/host-list', methods=['GET'])
def get_host_list():
    return jsonify({'host_list': list(client.known_hosts.keys())})


@app.route('/api/queue', methods=['POST'])
def add_song():
    global queue, playlist

    data = request.get_json()
    action = data.get('action')
    song = data.get('song')

    if action == "add":
        queue.append(song)
    elif action == "remove":
        queue.remove(song)

    msg = {
        "type": "queue",
        "action": action,
        "song": song
    }
    with client.lock:
        if client.known_hosts:
            name = list(client.known_hosts.keys())[0]
            target_ip = client.known_hosts[name]
            send_message_tcp(to=target_ip,
                            msg=msg,
                            port=config.MUSIC_PORT)

    response = {'message': 'Request received'}
    return response, 200


@app.route('/api/search', methods=['POST'])
def search_song():
    data = request.get_json()
    query = data.get('query')
    search_results = search.searchSong(query, topN=5)
    return jsonify({'search-results': search_results})


@app.route('/api/download', methods=['POST'])
def download_song():
    global queue, playlist, client
    
    data = request.get_json()
    url = data.get('url')
    status = search.downloadSong(url, './musics/')
    playlist.append(status)
    
    msg = {
        "type": "download",
        "link": url,
    }
    with client.lock:
        if client.known_hosts:
        
            name = list(client.known_hosts.keys())[0]
            target_ip = client.known_hosts[name]
            send_message_tcp(to=target_ip,
                            msg=msg,
                            port=config.MUSIC_PORT)

    response = {'message': status}
    return response, 200


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="SpotiLAN")

    parser.add_argument("-n", "--name", type=str, default=f"User{random.randint(1,15)}")
    queue = []
    playlist = []
    curr = 0
    client = Client(myname=parser.name)
    search = Searcher(songs=config.SONGS)

    for p in config.SONGS.keys():
        playlist.append("musics/"+p+".mp3")

    # Create threads
    threading.Thread(target=udp_broadcaster, args=()
                     ).start()  # udp broadcaster
    threading.Thread(target=udp_listener, args=()).start()  # udp listener
    threading.Thread(target=tcp_listener, args=(
        config.MSG_PORT,)).start()  # message listener
    threading.Thread(target=tcp_listener, args=(
        config.MUSIC_PORT,)).start()  # music listener
    threading.Thread(target=tcp_listener, args=(
        config.SYNC_PORT,)).start()  # sync listener
    threading.Thread(target=sync, args=(config.SYNC_PORT,)
                     ).start()  # sync listener
    # threading.Thread(target=clear_cache, args=()).start()  # clear cache

    # Flask app
    app.run()
