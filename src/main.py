import base64
import json
import os
import time
import socket
import flask
import select
import threading
import concurrent.futures

from src.configs import config
from src.utils.client import Client
from src.utils.search import Searcher
from src.utils.audio_player import AudioPlayer
from src.utils.messages import send_message_tcp, send_message_udp, process_tcp_msg, process_udp_msg

# Initialize global variables
client: Client
player: AudioPlayer
app = flask.Flask(__name__)

# Create a thread pool with a maximum of 10 threads
executor = concurrent.futures.ThreadPoolExecutor(max_workers=config.THREAD_POOL_SIZE)


def tcp_listener(
        port: int = config.MSG_PORT,
        buffer_size: int = config.BUFFER_SIZE,
):
    """
    Listens to the specified host:port socket for TCP messages and sends an answer if the message is valid.
    :param port: Port number to be listened
    :param buffer_size: size of the payload in package
    """
    global client
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
                executor.submit(process_tcp_msg, client, msg, addr[0])


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
                executor.submit(process_udp_msg, client, msg, sender[0], config.MSG_PORT)


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
        with client.lock:
            client.peer_sync_turn = False
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


def prompt() -> None:
    """
    Chat prompt handler
    """
    global client
    while True:
        curmsg = input().partition(":")
        # Exit feature
        if curmsg[1] != ':' and curmsg[0].strip() == "exit":
            print("Exited.")
            os._exit(1)
        # Messaging feature
        elif curmsg[0].strip() in client.known_hosts.keys():
            target_ip = client.known_hosts.get(curmsg[0].strip())
            if target_ip is not None:
                with client.lock:
                    message = {
                        'type': 'message',
                        'content': curmsg[2].strip()
                    }
                    send_message_tcp(to=target_ip, msg=message, port=config.PORT)
        else:
            print("This person does not exists!")


def sync(port: int = config.SYNC_PORT) -> None:
    """
    Constantly sending <SYNC> object
    TODO: Add turn flag
    """
    global client
    while True:
        if client.known_hosts:
            name = list(client.known_hosts.keys())[0]
            if client.peer_sync_turn:
                target_ip = client.known_hosts[name]
                message = {
                    "type": "sync",
                    "timestamp": time.perf_counter_ns(),
                }
                send_message_tcp(to=target_ip, msg=message, port=port)
                with client.lock:
                    client.peer_sync_turn = False


def player(action) -> None:
    """
    Chat prompt handler
    """
    pass


if __name__ == '__main__':
    client = Client(myname="daglar")
    # flask.g.update({"client": client})
    #
    # player = AudioPlayer()
    # flask.g.update({"player": player})
    #
    # search = Searcher()
    # flask.g.update({"search": search})

    # Create threads
    threading.Thread(target=udp_broadcaster, args=()).start()  # udp broadcaster
    threading.Thread(target=udp_listener, args=()).start()  # udp listener
    threading.Thread(target=tcp_listener, args=(config.MSG_PORT,)).start()  # message listener
    threading.Thread(target=tcp_listener, args=(config.SYNC_PORT,)).start()  # sync listener
    threading.Thread(target=sync, args=()).start()  # sync listener
    threading.Thread(target=clear_cache, args=()).start()  # clear cache

    # Flask app
    # app.run()
