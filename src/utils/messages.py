"""Contains utility functions for messaging"""
import socket
import json
import base64
import flask
import time
import numpy as np
from src.utils.client import Client
from src.utils.search import Searcher
import src.configs.config as config

import time
import threading
import multiprocessing
from pydub import AudioSegment, playback

global ff, queue


def send_message_tcp(to: str, msg: dict, port: int) -> None:
    """
    Sends the given `message` to the available hosts:port socket
    :param str to: Private host IP in the LAN
    :param dict msg: Message to be sent
    :param int port: Port number to be listened
    """
    msg = json.dumps(msg).encode('utf-8')
    msg = base64.b64encode(msg)
    # Create a socket object
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Set the timeout to 1 sec
        s.settimeout(0.5)
        try:
            # Establish connection
            s.connect((to, port))
            # Send message
            s.sendall(msg)
        except Exception as e:
            print(f'Unable to send message to {to}, {e=}')


def send_message_udp(
        msg: dict,
        port: int,
) -> None:
    """
    Broadcasts the hello message periodically
    :param dict msg: message to be broadcasted
    :param int port: Port number to broadcast
    """
    msg = json.dumps(msg).encode('UTF-8')
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.sendto(msg, ('<broadcast>', port))


def process_tcp_msg(
        msg: dict,
        host: str,
        client: Client = None,
        searcher: Searcher = None,
        queue: list = None,
        playlist: list = None,
        curr: int = None,
        curr_lock = None
):

    global ff

    if msg.get('type') == 'aleykumselam':
        with client.lock:
            client.add_known_host(ip=host, name=msg.get('myname'))

    elif msg.get('type') == 'message':
        with client.lock:
            idx = list(client.known_hosts.values()).index(host)
            name = list(client.known_hosts.keys())[idx]
        print(f"from {name} : {msg.get('content')}")

    elif msg["type"] == "start":
        # START CURRENT SONG
        with client.lock:
            agreed_time = int(msg.get("timestamp"))
            title = msg.get("title")
            peer_delay = np.mean(client.peer_delay)
            seg = AudioSegment.from_file(title)
            while True:
                if time.time_ns() >= agreed_time - int(peer_delay):
                    ff = playback._play_with_simpleaudio(seg)
                    break

    elif msg["type"] == "stop":
        with client.lock:
            agreed_time = int(msg.get("timestamp"))
            title = msg.get("title")
            peer_delay = np.mean(client.peer_delay)
            while True:
                if time.time_ns() >= agreed_time - int(peer_delay):
                    ff.stop()
                    break

    elif msg["type"] == "next":
        with client.lock:
            agreed_time = int(msg.get("timestamp"))
            title = msg.get("title")
            peer_delay = np.mean(client.peer_delay)
            seg = AudioSegment.from_file(title)
            while True:
                if time.time_ns() >= agreed_time - int(peer_delay):
                    ff.stop()
                    with curr_lock:
                        if curr == (len(playlist) - 1):
                            curr = 0
                        else:
                            curr += 1
                    ff = playback._play_with_simpleaudio(seg)
                    break

    elif msg["type"] == "previous":
        with client.lock:
            agreed_time = int(msg.get("timestamp"))
            title = msg.get("title")
            peer_delay = np.mean(client.peer_delay)
            seg = AudioSegment.from_file(title)
            while True:
                if time.time_ns() >= agreed_time - int(peer_delay):
                    ff.stop()
                    with curr_lock:
                        if curr == 0:
                            curr -= (len(playlist) - 1)
                        else:
                            curr -= 1

                    ff = playback._play_with_simpleaudio(seg)
                    break

    elif msg["type"] == "queue":
        action = msg.get("action")
        song_name = msg.get("song")
        if action == "add":
            queue.append(song_name)
        if action == "remove":
            queue.remove(song_name)

    elif msg["type"] == "download":
        url = msg.get("link")
        fname = searcher.downloadSong(url, "./musics/")
        playlist.append(fname)

    elif msg["type"] == "sync":
        timestamp = msg.get("timestamp")
        delay = time.time_ns() - timestamp
        name = list(client.known_hosts.keys())[0]
        with client.lock:
            meta_list = client.peer_delay[-config.DELAY_WINDOW:]
            meta_list.append(int(delay))
            client.peer_delay = meta_list

    else:
        raise Exception(f"Invalid message type {msg.get('type')}")


def process_udp_msg(
        client: Client,
        msg: bytes,
        host: str,
        port: int
):
    msg = json.loads(msg.decode('utf-8'))
    if msg.get('type') == 'hello':
        with client.lock:
            client.add_known_host(ip=host, name=msg.get('myname'))
        resp = {'type': 'aleykumselam', 'myname': f'{client.myname}'}
        send_message_tcp(to=host, msg=resp, port=port)
