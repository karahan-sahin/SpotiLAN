"""Contains utility functions for messaging"""
import socket
import json
import base64

from src.utils.client import Client


def send_message_tcp(to: str, msg: dict, port: int, ) -> None:
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
        s.settimeout(1.0)
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
        client: Client,
        msg: dict,
        host: str,
):
    if msg.get('type') == 'aleykumselam':
        with client.lock:
            client.add_known_host(ip=host, name=msg.get('myname'))
    elif msg.get('type') == 'message':
        with client.lock:
            idx = list(client.known_hosts.values()).index(host)
            name = list(client.known_hosts.keys())[idx]
        print(f"from {name} : {msg.get('content')}")
    elif msg["type"] == "strat":
        pass  # START CURRENT SONG
    elif msg["type"] == "stop":
        pass  # STOP CURRENT SONG
    elif msg["type"] == "change":
        pass  # CHANGE SONG AT PLAYLIST
    elif msg["type"] == "add":
        pass  # ADD SONGS TO PLAYLIST
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

# def udp_message_handler(
#         client: Client,
#         msg: Union[bytes, dict],
#         in_ip: str
# ):
#     """
#     Receives a message decides whether hosts are met before
#     :param Client client: Identity object that contains myip and myname field
#     :param dict msg: Incoming message as string
#     :param str in_ip: Incoming messages' sender ip
#     :return: None if a.s. message, otherwise answer
#     """
#     if isinstance(msg, bytes):
#         msg = json.loads(msg.decode('utf-8'))
#     elif isinstance(msg, str):
#         msg = json.loads(msg)
#     try:
#         if msg.get('type') == 'hello':
#             with client.lock:
#                 client.add_new_host(ip=in_ip, name=msg.get('myname'))
#                 resp = {'type': 'aleykumselam', 'myname': f'{client.myname}'}
#             return resp
#         else:
#             print(f"Invalid type: {msg.get('type')}")
#             return dict()
#     except Exception as e:
#         print(f'Error occurred {e=}')
#         return
