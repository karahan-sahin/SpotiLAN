import base64
import json
import os
import time
import socket
import select
import threading
import concurrent.futures

from src.app import app, set_params
from src.configs import config
from src.utils.client import Client
from src.messages.messages import send_message_tcp, send_message_udp, process_tcp_msg, process_udp_msg

# Initialize global variables
client: Client

# Create a thread pool with a maximum of 10 threads
executor = concurrent.futures.ThreadPoolExecutor(max_workers=config.THREAD_POOL_SIZE)


def tcp_listener(
        port: int = config.PORT,
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
        port: int = config.PORT,
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
                executor.submit(process_udp_msg, client, msg, sender[0], config.PORT)


def udp_broadcaster(
        port: int = config.PORT,
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


if __name__ == '__main__':
    # Set the myname
    # while True:
    #     myname = input("Name: ").strip()
    #     if myname.isalnum():
    #         client = Client(myname=myname)
    #         print(f"Welcome {client.myname}")
    #         break
    #     else:
    #         print("Please enter a valid name!")
    #
    client = Client(myname="daglar")
    # Create threads
    threading.Thread(target=udp_broadcaster, args=()).start()  # udp broadcaster
    threading.Thread(target=udp_listener, args=()).start()  # udp listener
    threading.Thread(target=tcp_listener, args=()).start()  # tcp listener
    threading.Thread(target=clear_cache, args=()).start()  # clear cache

    # Flask app

    set_params(c=client)
    app.run()
